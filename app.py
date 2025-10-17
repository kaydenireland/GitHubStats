from flask import Flask, jsonify, request, send_file
from flask_restful import Resource, Api
from trending_repos import scraper
from top_langs import repo_lang_analysis, grapher
from pathlib import Path
import io

# Create Flask App
app = Flask(__name__)
# Create API Object
api = Api(app)


class Hello(Resource):

    def get(self):
        return {"Message": "Hello World"}

class Trending(Resource):

    def get(self):
        lang = request.args.get("lang", "").strip().lower()

        repos = scraper.get_repos(lang)
        return jsonify([repo.to_dict() for repo in repos])

class RepoTopLangs(Resource):

    def get(self, username):
        # Fetch Lang Returns Dict
        lang_data = repo_lang_analysis.fetch_new_langs(username)

        chart_type = request.args.get("chart", "donut") # pie, donut, vbar, hbar, stacked
        output_type = request.args.get("output", "json") # json, graph

        if output_type == "json":
            return jsonify(lang_data)

        elif output_type == "graph":
            cfp = Path(__file__).resolve().parent / "top_langs" / "lang_colors.json"
            print(cfp)
            fig, _ = grapher.create_chart(
                chart_type,
                username,
                lang_data,
                minimum_percentage = .005,
                dh_width = .3,
                color_file_path = cfp
            )

            fig_io = io.BytesIO()
            fig.savefig(fig_io, format = "PNG", bbox_inches = "tight")
            fig_io.seek(0)
            return send_file(fig_io, mimetype = "image/png")

        else:
            return {"error", "Invalid Output Type"}, 400



# Add Defined Resource & Corresponding Urls
api.add_resource(Hello, "/")
api.add_resource(Trending, "/trending/")
api.add_resource(RepoTopLangs, "/toplangs/repo/<string:username>")
