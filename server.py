import uvicorn

if __name__ == '__main__':
    uvicorn.run("project_reports_akz.asgi:application", reload=True)