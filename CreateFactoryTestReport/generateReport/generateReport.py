import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from flask import Flask, jsonify, request


class GenerateReport(object):

    def __init__(self, app, render_pdf=False):
        self.render_pdf = render_pdf
        self.app = app
        self.app.add_url_rule('/puzzle/api/v1/create_report', 'report_api', self.report_api, methods=['POST'])
        self.elements = []
        self.styles = getSampleStyleSheet()
        self.ts = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C0C0C0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E0E0E0')])
        ]
        self.project_path = os.path.dirname(os.path.realpath(__file__))

    def labelfont_prop(self):
        font_prop = {'family': 'serif',
                    'color': 'black',
                    'weight': 'bold',
                    'size': 12,
                    }
        return font_prop

    def tickfont_prop(self):
        font_prop = {'family': 'serif',
                    'color': 'black',
                    'weight': 'bold',
                    'size': 9,
                    }
        return font_prop

    def throughput_bar_chart(self, df, outdir, filename):
        ax = df.plot.bar(rot=0, fontsize=12)
        ax.set_xlabel("NICS", fontdict=self.labelfont_prop())
        ax.set_ylabel("Throughput (Mbps)", fontdict=self.labelfont_prop())
        # ax.get_legend().remove()
        plt.tight_layout()
        plt.savefig(outdir + "/" + filename, dpi=600)

    def draw_line(self, color):
        d = Drawing(100, 1)
        d.add(Line(0, 0, 533, 0, strokeColor=color))
        return d

    def heading_block(self, name=None):
        h1 = ParagraphStyle(name='Heading1',
                            # fontName='Times-Roman',
                            fontSize=14,
                            leading=18,
                            backColor=colors.lightgrey,
                            textColor=colors.black,
                            alignment=TA_LEFT)
        # self.elements.append(self.draw_line(colors.grey))
        # self.elements.append(Paragraph('<font backColor={}><b> {} </b></font>'.format(colors.lightgrey, name), h1))
        self.elements.append(Paragraph('<b> {} </b>'.format(name), h1))
        self.elements.append(self.draw_line(colors.black))
        self.elements.append(Spacer(1, 12))

    def draw_table(self, data, column=None):
        try:
            if isinstance(data, list) or isinstance(data, dict):
                df = pd.DataFrame.from_dict(data)
                df.replace("", "N/A", inplace=True)
                df = df[column]
                df.columns = [x.title() for x in column]
                lista = [df.columns.values.astype(str).tolist()] + df.values.tolist()
            elif isinstance(data, pd.DataFrame):
                lista = [data.reset_index().columns.values.astype(str).tolist()] + data.reset_index().values.tolist()
            else:
                logging.error("Unknown Type")
            table = Table(lista, style=self.ts)
            table.hAlign = "LEFT"
            self.elements.append(table)
            self.elements.append(Spacer(1, 20))
        except Exception as e:
            logging.error("Error in creating table. " + str(e))

    def create_report(self, info):
        # Converting to PDF
        # document theme
        if local:
            doc = SimpleDocTemplate('{}_TestReport.pdf'.format(info["serialNo"]))
        else:
            doc = SimpleDocTemplate('/home/test/reports/{}_TestReport.pdf'.format(info["serialNo"]))
        doc.topMargin = 20
        doc.bottomMargin = 25
        doc.leftMargin = 25
        doc.rightMargin = 25
        doc.allowSplitting = False

        header_path = self.project_path + "/" + "header.png"
        if os.path.exists(header_path):
            header = Image(header_path, 8 * inch, 1 * inch)
            header.hAlign = "CENTRE"
            self.elements.append(header)
            self.elements.append(Spacer(1, 20))
        else:
            logging.warning("Header not found")

        self.elements.append(self.draw_line(colors.lightgrey))
        self.elements.append(Spacer(1, 1))
        self.elements.append(self.draw_line(colors.lightgrey))
        self.elements.append(Spacer(1, 3))
        self.elements.append(Paragraph("Serial No: " + info["serialNo"], self.styles['Title']))
        self.elements.append(self.draw_line(colors.lightgrey))
        self.elements.append(Spacer(1, 1))
        self.elements.append(self.draw_line(colors.lightgrey))
        self.elements.append(Spacer(1, 20))

        # Create Tables for each test

        # Device Info Table
        if info["deviceInfo"]:
            self.heading_block("Device Info")
            dev_table = pd.DataFrame(info["deviceInfo"], index=[0])
            dev_table = dev_table.T
            dev_table.reset_index(inplace=True)
            dev_table.columns = ["Item", "Detail"]
            dev_table.set_index(["Item"], inplace=True)
            dev_table.replace("", "N/A", inplace=True)
            self.draw_table(dev_table)

        # Mac Table
        if info["macInfo"]:
            self.heading_block("MAC Info")
            self.draw_table(info["macInfo"], column=["interface", "macaddr"])

        # Operation Table
        if info["operationInfo"]:
            self.heading_block("Operation Details")
            opt_table = pd.DataFrame(info["operationInfo"], index=[0])
            opt_table = opt_table.T
            opt_table.reset_index(inplace=True)
            opt_table.columns = ["Operation", "Status"]
            opt_table.set_index(["Operation"], inplace=True)
            opt_table.replace("", "N/A", inplace=True)
            self.draw_table(opt_table)

        # Test Table
        if info["testInfo"]:
            self.heading_block("Test Details")
            test_table = pd.DataFrame(info["testInfo"], index=[0])
            test_table = test_table.T
            test_table.reset_index(inplace=True)
            test_table.columns = ["Test", "Status"]
            test_table.set_index(["Test"], inplace=True)
            test_table.replace("", "N/A", inplace=True)
            self.draw_table(test_table)

        # Hardware Test Table

        if info["hwtestInfo"]:
            self.heading_block("Hardware Test Details")
            self.draw_table(info["hwtestInfo"], column=["item", "result", "detail"])

        # Burn test details
        if info["burntestInfo"]:
            self.heading_block("Burn Test Details")
            self.draw_table(info["burntestInfo"], column=["item", "result", "detail"])

        # Last test details
        if info["lasttestInfo"]:
            self.heading_block("Last Test Details")
            self.draw_table(info["lasttestInfo"], column=["item", "result", "detail"])

        # LanBurn Throughput Table
        self.heading_block("LanBurn Throughput")
        speed_table = pd.DataFrame.from_dict(info["performancestatsInfo"])
        speed_table.columns = [x.title() for x in speed_table.columns]
        speed_table.set_index(["Nic"], inplace=True)
        self.draw_table(speed_table)

        # LanBurn Throughput Bar Chart
        self.elements.append(Spacer(1, 30))
        filename = "lanburn.png"
        self.throughput_bar_chart(speed_table, self.project_path, filename)
        im = Image(filename, 4 * inch, 2.5 * inch)
        self.elements.append(im)

        if self.render_pdf:
            # Build all the elements to create a PDF
            doc.build(self.elements)

    def report_api(self):
        try:
            if local:
                import chumma
                info = chumma.data
            else:
                info = request.get_json()
            self.create_report(info)
            resp = {"msg": "PDF successfully rendered"}
            if local:
                print("Test Report generated. Find in {}\{}_TestReport.pdf".format(
                    self.project_path, info["serialNo"]))
            else:
                logging.info("Test Report generated. Find in /home/test/reports/{}_TestReport.pdf".format(
                    info["serialNo"]))
        except Exception as e:
            resp = {"msg": str(type(e).__name__) + str(e)}
            logging.error(resp)
        return jsonify(resp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    local = False
    app = Flask(__name__)
    GenerateReport(app, render_pdf=True)
    app.run(host='0.0.0.0', port=6662, debug=True)
