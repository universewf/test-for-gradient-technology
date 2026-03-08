import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Post
from cache import redis
from schemas import PostRead


# --- CREATE ---
async def create_post(db: AsyncSession, title: str, content: str):
    new_post = Post(title=title, content=content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    await redis.delete("posts_all")
    return new_post


# --- READ ALL ---
async def get_all_posts(db: AsyncSession):
    cached = await redis.get("posts_all")
    if cached:
        return [PostRead(**item) for item in json.loads(cached)]

    result = await db.execute(select(Post))
    posts = result.scalars().all()

    await redis.set(
        "posts_all",
        json.dumps([{"id": p.id, "title": p.title, "content": p.content} for p in posts]),
        ex=300,
    )
    return posts


# --- READ ONE ---
async def get_post(db: AsyncSession, post_id: int):
    cached = await redis.get(f"post:{post_id}")
    if cached:
        return PostRead(**json.loads(cached))

    post = await db.get(Post, post_id)
    if not post:
        return None

    await redis.set(
        f"post:{post_id}",
        json.dumps({"id": post.id, "title": post.title, "content": post.content}),
        ex=300,
    )
    return post


# --- UPDATE ---
async def update_post(db: AsyncSession, post_id: int, title: str, content: str):
    db_post = await db.get(Post, post_id)
    if not db_post:
        return None

    db_post.title = title
    db_post.content = content
    await db.commit()
    await db.refresh(db_post)

    await redis.delete(f"post:{post_id}")
    await redis.delete("posts_all")
    return db_post


# --- DELETE ---
async def delete_post(db: AsyncSession, post_id: int):
    db_post = await db.get(Post, post_id)
    if not db_post:
        return None

    await db.delete(db_post)
    await db.commit()

    await redis.delete(f"post:{post_id}")
    await redis.delete("posts_all")
    return True
