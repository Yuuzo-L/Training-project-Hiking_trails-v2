import subprocess

def generate_requirements():
    with open("requirements.txt", "w", encoding="utf-8") as f:
        output = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
        f.write(output)
    print("✅ 已產生 requirements.txt")

def generate_render_yaml():
    content = """\
services:
  - type: web
    name: trail-app
    runtime: python
    buildCommand: ""
    startCommand: "python app.py"
    envVars:
      - key: FLASK_ENV
        value: production
"""
    with open("render.yaml", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 已產生 render.yaml")

if __name__ == "__main__":
    generate_requirements()
    generate_render_yaml()
