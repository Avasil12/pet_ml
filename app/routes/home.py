from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from models.user import RegistrationForm, User
from auth.authenticate import authenticate_cookie
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from database.database import get_session
from services.auth.loginform import LoginForm
from services.crud import user as UsersService
from database.config import get_settings

settings = get_settings()
home_route = APIRouter()
hash_password = HashPassword()
templates = Jinja2Templates(directory="view")


@home_route.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        user = await authenticate_cookie(token)
    else:
        user = None

    context = {
        "user": user,
        "request": request
    }
    return templates.TemplateResponse("index.html", context)


@home_route.get("/private", response_class=HTMLResponse)
async def index_private(request: Request, user:str=Depends(authenticate_cookie)):
    context = {
        "user": user,
        "request": request
    }
    return templates.TemplateResponse("private.html", context)


@home_route.get("/private2", response_class=HTMLResponse)
async def index_private2(request: Request):
    context = {
        "user": 'user',
        "request": request
    }
    return templates.TemplateResponse("private.html", context)


@home_route.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm=Depends(), session=Depends(get_session)) -> dict[str, str]:    
    user_exist = UsersService.get_user_by_email(form_data.username, session)
    if user_exist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    if hash_password.verify_hash(form_data.password, user_exist.password):
        access_token = create_access_token(user_exist.email)
        response.set_cookie(
            key=settings.COOKIE_NAME, 
            value=f"Bearer {access_token}", 
            httponly=True
        )
        
        # return {"access_token": access_token, "token_type": "Bearer"}
        return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )


@home_route.get("/auth/register", response_class=HTMLResponse)
async def register_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("register.html", context)


@home_route.post("/auth/register", response_class=HTMLResponse)
async def register_post(request: Request, session=Depends(get_session)):
    form_data = await request.form()    
    form_dict = {
        "email": form_data.get("email"),
        "password": form_data.get("password"),
    }
    errors = []

    try:
        registration_form = RegistrationForm(**form_dict)
    except ValidationError as e:
        errors = e.errors()
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors, "email": form_dict.get("email")})

    user_exist = UsersService.get_user_by_email(registration_form.email, session)
    if user_exist:
        errors.append({"loc": ["email"], "msg": "User with this email already exists."})
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors, "email": registration_form.email})

    hashed_password = hash_password.create_hash(registration_form.password)
    user_data = User(email=registration_form.email, password=hashed_password)  # Создание экземпляра модели
    UsersService.create_user(user_data, session)  # Передаем экземпляр модели

    response = RedirectResponse("/", status.HTTP_302_FOUND)
    access_token = create_access_token(registration_form.email)
    response.set_cookie(key=settings.COOKIE_NAME, value=f"Bearer {access_token}", httponly=True)

    return response



@home_route.get("/auth/login", response_class=HTMLResponse)
async def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)
    

@home_route.post("/auth/login", response_class=HTMLResponse)
async def login_post(request: Request, session=Depends(get_session)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form, session=session)
            form.__dict__.update(msg="Login Successful!")
            print("[green]Login successful!!!!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


@home_route.get("/auth/logout", response_class=HTMLResponse)
async def login_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


@home_route.get('/test')
async def test():
    return {"message": "success"}
