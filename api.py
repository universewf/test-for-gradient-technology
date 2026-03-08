from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import PostCreate, PostRead
from crud import create_post, get_post, get_all_posts, update_post, delete_post

router = APIRouter()


@router.post("/posts/", response_model=PostRead, summary="Создать пост")
async def api_create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    return await create_post(db, post.title, post.content)


@router.get("/posts/", response_model=list[PostRead], summary="Получить все посты")
async def api_get_all_posts(db: AsyncSession = Depends(get_db)):
    return await get_all_posts(db)


@router.get("/posts/{post_id}", response_model=PostRead, summary="Получить пост по ID")
async def api_get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return post


@router.put("/posts/{post_id}", response_model=PostRead, summary="Обновить пост")
async def api_update_post(post_id: int, post: PostCreate, db: AsyncSession = Depends(get_db)):
    db_post = await update_post(db, post_id, post.title, post.content)
    if not db_post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return db_post


@router.delete("/posts/{post_id}", status_code=204, summary="Удалить пост")
async def api_delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_post(db, post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return Response(status_code=204)
