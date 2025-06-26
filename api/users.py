from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    # 这里简化处理，实际应该有密码加密和用户验证
    from models.models import User as UserModel
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # 检查用户是否已存在
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    
    # 创建新用户
    hashed_password = pwd_context.hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=User)
def get_current_user(db: Session = Depends(get_db)):
    """获取当前用户信息"""
    # 这里简化处理，假设用户ID为1，实际应该有用户认证
    from models.models import User as UserModel
    user = db.query(UserModel).filter(UserModel.id == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user 