import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from flask import Flask, after_this_request, jsonify, render_template, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(ok=True, engine=shutil.which("ODAFileConverter") is not None)


@app.post("/optimize")
def optimize():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify(error="请选择 DWG 文件"), 400
    if not uploaded.filename.lower().endswith(".dwg"):
        return jsonify(error="仅支持 .dwg 文件"), 400

    version = request.form.get("version", "ACAD2018")
    if version not in {"ACAD2018", "ACAD2013", "ACAD2010"}:
        version = "ACAD2018"

    work = Path(tempfile.mkdtemp(prefix="dwg-slim-"))
    source_dir = work / "in"
    output_dir = work / "out"
    source_dir.mkdir()
    output_dir.mkdir()

    safe_name = secure_filename(uploaded.filename) or "drawing.dwg"
    if not safe_name.lower().endswith(".dwg"):
        safe_name += ".dwg"
    source = source_dir / safe_name
    uploaded.save(source)

    try:
        command = [
            "xvfb-run", "-a", "ODAFileConverter",
            str(source_dir), str(output_dir), version, "DWG", "0", "1", "*.dwg"
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=240)
        output = output_dir / safe_name
        if result.returncode != 0 or not output.exists() or output.stat().st_size == 0:
            message = (result.stderr or result.stdout or "转换失败")[-1200:]
            raise RuntimeError(message)

        original_size = source.stat().st_size
        new_size = output.stat().st_size
        download_name = f"{Path(safe_name).stem}_slim.dwg"

        @after_this_request
        def cleanup(response):
            shutil.rmtree(work, ignore_errors=True)
            response.headers["X-Original-Size"] = str(original_size)
            response.headers["X-Optimized-Size"] = str(new_size)
            return response

        return send_file(output, as_attachment=True, download_name=download_name,
                         mimetype="application/acad")
    except subprocess.TimeoutExpired:
        shutil.rmtree(work, ignore_errors=True)
        return jsonify(error="处理超时，请稍后重试"), 504
    except Exception as exc:
        shutil.rmtree(work, ignore_errors=True)
        return jsonify(error=f"处理失败：{exc}"), 500


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="文件不能超过 100 MB"), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
