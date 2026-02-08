from flask import Flask, render_template, request, jsonify, send_file
from inheritance_logic import calculate_inheritance
from pdf_report import generate_pdf
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        received = request.json
        logging.info(f"Received payload: {received}")

        # Normalize and validate inputs
        if not received or "estate" not in received:
            return jsonify({"error": "قيمة التركة مطلوبة"}), 400

        data = {}
        # numeric coercions with safe defaults
        try:
            data["estate"] = float(received.get("estate", 0))
        except Exception:
            return jsonify({"error": "قيمة التركة غير صحيحة"}), 400

        if data["estate"] <= 0:
            return jsonify({"error": "قيمة التركة يجب أن تكون أكبر من صفر"}), 400

        data["deceased_gender"] = received.get("deceased_gender", "ذكر")
        # spouse fields
        data["husband"] = bool(received.get("husband", False))
        try:
            data["wives"] = int(received.get("wives", 0))
        except Exception:
            data["wives"] = 0

        # relatives counts / flags
        data["father"] = bool(received.get("father", False))
        data["mother"] = bool(received.get("mother", False))
        data["sons"] = int(received.get("sons", 0) or 0)
        data["daughters"] = int(received.get("daughters", 0) or 0)
        data["brothers"] = int(received.get("brothers", 0) or 0)
        data["sisters"] = int(received.get("sisters", 0) or 0)
        data["grandfather"] = bool(received.get("grandfather", False))
        data["grandmother"] = bool(received.get("grandmother", False))
        data["halfbrothers_father"] = int(received.get("halfbrothers_father", 0) or 0)
        data["halfsisters_father"] = int(received.get("halfsisters_father", 0) or 0)

        # Enforce consistency: only one spouse type based on deceased gender
        if data["deceased_gender"] == "ذكر":
            # deceased male -> there is no husband
            data["husband"] = False
        else:
            # deceased female -> no wives
            data["wives"] = 0

        logging.info(f"Normalized payload: {data}")

        shares, explanation = calculate_inheritance(data)

        return jsonify({
            "labels": list(shares.keys()),
            "values": [round(v, 2) for v in shares.values()],
            "explanation": explanation,
            "raw_received": received,
            "raw_normalized": data
        })
    except Exception as e:
        logging.error(f"Error in calculate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/pdf", methods=["POST"])
def pdf():
    try:
        data = request.json
        shares, explanation = calculate_inheritance(data)
        filename = "inheritance_report.pdf"
        generate_pdf(filename, data["estate"], explanation)
        return send_file(filename, as_attachment=True, download_name="تقرير_المواريث.pdf")
    except Exception as e:
        logging.error(f"Error in pdf: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "الصفحة غير موجودة"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "خطأ في الخادم"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
