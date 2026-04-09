import os
import psycopg2
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
APP_NAME = os.getenv("APP_NAME", "Base_App")

def get_db_conn():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT, is_done BOOLEAN DEFAULT FALSE);")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/api/status")
async def get_status():
    return {"status": "online", "node_name": APP_NAME}

@app.get("/", response_class=HTMLResponse)
async def index():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    tasks_li = ""
    for r in rows:
        # r[0] - id, r[1] - title, r[2] - is_done
        is_done = r[2] 
        checked = "checked" if is_done else ""
    # Добавим стиль зачеркивания для выполненных задач
        text_style = "text-decoration: line-through; color: #888;" if is_done else "color: #333;"
    
        tasks_li += f"""
        <li style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding: 5px 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <input type="checkbox" {checked} onchange="window.location.href='/toggle/{r[0]}'" style="cursor: pointer; width: 18px; height: 18px;">
                <span style="{text_style}">{r[1]}</span>
            </div>
            <div>
                <a href='/edit_form/{r[0]}' style='color:orange; text-decoration:none; margin-right:10px;'>[Изменить]</a>
                <a href='/del/{r[0]}' style='color:red; text-decoration:none;'>[Удалить]</a>
            </div>
        </li>"""
    
    return f"""
    <html>
        <body style="font-family: sans-serif; padding: 40px; background: #f4f4f4;">
            <div style="max-width: 500px; margin: auto; background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #333;">Список задач</h2>
                <form action="/add" method="post" style="display: flex; gap: 10px;">
                    <input name="title" placeholder="Текст задачи..." required style="flex-grow: 1; padding: 8px;">
                    <button type="submit" style="cursor: pointer; background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 4px;">+</button>
                </form>
                <hr style="margin: 20px 0; border: 0; border-top: 1px solid #ddd;">
                <ul style="padding: 0; list-style: none;">{tasks_li if tasks_li else "Список пуст"}</ul>
            </div>
        </body>
    </html>
    """

@app.post("/add")
async def add(title: str = Form(...)):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
    conn.commit()
    cur.close()
    conn.close()
    return HTMLResponse("<script>location.href='/'</script>")

# Форма для редактирования (окно)
@app.get("/edit_form/{idx}", response_class=HTMLResponse)
async def edit_form(idx: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT title FROM tasks WHERE id = %s", (idx,))
    task_title = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"""
    <html>
        <body style="font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f4f4;">
            <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3>Редактировать задачу</h3>
                <form action="/update/{idx}" method="post">
                    <input name="new_title" value="{task_title}" required style="padding: 8px; width: 250px;">
                    <button type="submit" style="padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Сохранить</button>
                </form>
                <br>
                <a href="/" style="color: #666; text-decoration: none;">Назад</a>
            </div>
        </body>
    </html>
    """

@app.post("/update/{idx}")
async def update(idx: int, new_title: str = Form(...)):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET title = %s WHERE id = %s", (new_title, idx))
    conn.commit()
    cur.close()
    conn.close()
    return HTMLResponse("<script>location.href='/'</script>")

@app.get("/del/{idx}")
async def delete(idx: int):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (idx,))
    conn.commit()
    cur.close()
    conn.close()
    return HTMLResponse("<script>location.href='/'</script>")
@app.get("/toggle/{idx}")
async def toggle_task(idx: int):
    conn = get_db_conn()
    cur = conn.cursor()
    # SQL магия: меняем значение на противоположное (True -> False, False -> True)
    cur.execute("UPDATE tasks SET is_done = NOT is_done WHERE id = %s", (idx,))
    conn.commit()
    cur.close()
    conn.close()
    return HTMLResponse("<script>location.href='/'</script>")