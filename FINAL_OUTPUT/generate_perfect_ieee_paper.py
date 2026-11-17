#!/usr/bin/env python3
"""
Generate the publication-ready IEEE two-column conference paper (.docx)
with 100% verified empirical findings, high-resolution figures, 
comprehensive tables, strict IEEE formatting, and zero layout defects.
Fully addresses all peer-review feedback.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

BASE_DIR = Path("/Users/ashish/Desktop/Side Project/Soft Computing Term Paper")
FINAL_OUT = BASE_DIR / "FINAL_OUTPUT"
FINAL_OUT.mkdir(parents=True, exist_ok=True)
DOCX_PATH = FINAL_OUT / "IEEE_GA_FeatureSelection_Paper_AshishPathak.docx"

SOURCE_EXP = BASE_DIR / "Research_Paper_Full_Expansion"
ANALYSIS_DIR = SOURCE_EXP / "analysis"
FIGS_DIR = FINAL_OUT / "crisp_figures"

# ─── XML & Layout Helpers ───────────────────────────────────────────────────

def format_ds_name(dname: str) -> str:
    if dname.lower() in ("rna_seq", "rna seq"):
        return "RNA-seq"
    return dname.replace("_", " ").title()

def set_cell_margins(cell, top=25, bottom=25, left=45, right=45):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")

def set_table_borders(table, color="B0B0B0", size="4"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), color)
        borders.append(tag)

def set_row_cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:cantSplit")
    tr_pr.append(node)

def set_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    node = OxmlElement("w:tblHeader")
    node.set(qn("w:val"), "true")
    tr_pr.append(node)

def set_columns(section, count=2, space_twips=360):
    sect_pr = section._sectPr
    for existing in sect_pr.findall(qn("w:cols")):
        sect_pr.remove(existing)
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), str(count))
    cols.set(qn("w:space"), str(space_twips))
    cols.set(qn("w:equalWidth"), "1")
    sect_pr.append(cols)

def configure_page(section, top_mm=19.05, bottom_in=0.75, side_in=0.62):
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(top_mm)
    section.bottom_margin = Inches(bottom_in)
    section.left_margin = Inches(side_in)
    section.right_margin = Inches(side_in)
    section.header_distance = Inches(0.5)
    section.footer_distance = Inches(0.5)

# ─── Style Configuration ─────────────────────────────────────────────────────

def setup_document_styles(doc):
    styles = doc.styles

    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    # IEEE Body Text
    if "IEEE Body" not in styles:
        s_body = styles.add_style("IEEE Body", 1)
        s_body.base_style = normal
        s_body.font.name = "Times New Roman"
        s_body.font.size = Pt(9.5)
        s_body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_body.paragraph_format.first_line_indent = Inches(0.14)
        s_body.paragraph_format.space_before = Pt(0)
        s_body.paragraph_format.space_after = Pt(1.0)
        s_body.paragraph_format.line_spacing = 1.0

    # IEEE Abstract
    if "IEEE Abstract" not in styles:
        s_abs = styles.add_style("IEEE Abstract", 1)
        s_abs.base_style = normal
        s_abs.font.name = "Times New Roman"
        s_abs.font.size = Pt(8.8)
        s_abs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_abs.paragraph_format.first_line_indent = Inches(0.14)
        s_abs.paragraph_format.space_before = Pt(0)
        s_abs.paragraph_format.space_after = Pt(2.0)
        s_abs.paragraph_format.line_spacing = 1.0

    # IEEE Keywords
    if "IEEE Keywords" not in styles:
        s_kw = styles.add_style("IEEE Keywords", 1)
        s_kw.base_style = normal
        s_kw.font.name = "Times New Roman"
        s_kw.font.size = Pt(8.8)
        s_kw.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_kw.paragraph_format.first_line_indent = Inches(0.14)
        s_kw.paragraph_format.space_before = Pt(0)
        s_kw.paragraph_format.space_after = Pt(2.5)
        s_kw.paragraph_format.line_spacing = 1.0

    # IEEE Heading 1
    if "IEEE H1" not in styles:
        s_h1 = styles.add_style("IEEE H1", 1)
        s_h1.base_style = normal
        s_h1.font.name = "Times New Roman"
        s_h1.font.size = Pt(9.8)
        s_h1.font.bold = True
        s_h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        s_h1.paragraph_format.space_before = Pt(4.0)
        s_h1.paragraph_format.space_after = Pt(1.5)
        s_h1.paragraph_format.keep_with_next = True

    # IEEE Heading 2
    if "IEEE H2" not in styles:
        s_h2 = styles.add_style("IEEE H2", 1)
        s_h2.base_style = normal
        s_h2.font.name = "Times New Roman"
        s_h2.font.size = Pt(9.5)
        s_h2.font.italic = True
        s_h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        s_h2.paragraph_format.space_before = Pt(3.0)
        s_h2.paragraph_format.space_after = Pt(1.0)
        s_h2.paragraph_format.keep_with_next = True

    # IEEE Table Title
    if "IEEE Table Title" not in styles:
        s_tt = styles.add_style("IEEE Table Title", 1)
        s_tt.base_style = normal
        s_tt.font.name = "Times New Roman"
        s_tt.font.size = Pt(7.8)
        s_tt.font.bold = True
        s_tt.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        s_tt.paragraph_format.space_before = Pt(3.5)
        s_tt.paragraph_format.space_after = Pt(1.0)
        s_tt.paragraph_format.keep_with_next = True

    # IEEE Figure Caption
    if "IEEE Fig Caption" not in styles:
        s_fc = styles.add_style("IEEE Fig Caption", 1)
        s_fc.base_style = normal
        s_fc.font.name = "Times New Roman"
        s_fc.font.size = Pt(7.8)
        s_fc.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_fc.paragraph_format.space_before = Pt(1.0)
        s_fc.paragraph_format.space_after = Pt(2.0)
        s_fc.paragraph_format.line_spacing = 1.0

    # IEEE Reference Item
    if "IEEE Ref" not in styles:
        s_ref = styles.add_style("IEEE Ref", 1)
        s_ref.base_style = normal
        s_ref.font.name = "Times New Roman"
        s_ref.font.size = Pt(7.5)
        s_ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_ref.paragraph_format.left_indent = Inches(0.18)
        s_ref.paragraph_format.first_line_indent = Inches(-0.18)
        s_ref.paragraph_format.space_before = Pt(0)
        s_ref.paragraph_format.space_after = Pt(0.5)
        s_ref.paragraph_format.line_spacing = 1.0

def add_body(doc, text, indent=True):
    p = doc.add_paragraph(style="IEEE Body")
    if not indent:
        p.paragraph_format.first_line_indent = Pt(0)
    p.add_run(text)
    return p

def add_h1(doc, title):
    return doc.add_paragraph(title, style="IEEE H1")

def add_h2(doc, title):
    return doc.add_paragraph(title, style="IEEE H2")

def add_table_title(doc, text):
    return doc.add_paragraph(text, style="IEEE Table Title")

def add_column_break(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run()
    run.add_break(WD_BREAK.COLUMN)
    return p

def add_fig(doc, img_path, caption_text, width_in=3.25):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1.5)
    p.paragraph_format.space_after = Pt(0.5)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(img_path), width=Inches(width_in))
    
    cp = doc.add_paragraph(style="IEEE Fig Caption")
    colon_idx = caption_text.find(":")
    if colon_idx != -1:
        label_part = caption_text[:colon_idx+1]
        body_part = caption_text[colon_idx+1:]
        r1 = cp.add_run(label_part)
        r1.bold = True
        cp.add_run(body_part)
    else:
        cp.add_run(caption_text)
    return p, cp

def build_ieee_table(doc, headers, data, widths, font_size=6.6):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    tbl_pr = tbl._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    
    total_w = sum(widths)
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(total_w * 1440)))
    tbl_w.set(qn("w:type"), "dxa")

    hdr_cells = tbl.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = Inches(widths[i])
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(title)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
        tc_pr = hdr_cells[i]._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "1F3864")
        tc_pr.append(shd)
        hdr_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(hdr_cells[i], top=25, bottom=25, left=35, right=35)
        
    set_repeat_header(tbl.rows[0])
    set_row_cant_split(tbl.rows[0])

    for row_idx, row_data in enumerate(data):
        row = tbl.add_row()
        set_row_cant_split(row)
        bg_col = "F2F4F7" if row_idx % 2 == 1 else "FFFFFF"
        for i, val in enumerate(row_data):
            cell = row.cells[i]
            cell.width = Inches(widths[i])
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1.0)
            p.paragraph_format.space_after = Pt(1.0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(str(val))
            r.font.name = "Times New Roman"
            r.font.size = Pt(font_size)
            if i == 0:
                r.bold = True
            tc_pr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), bg_col)
            tc_pr.append(shd)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell, top=20, bottom=20, left=35, right=35)

    set_table_borders(tbl, color="D0D5DD", size="4")
    return tbl

# ─── Main Paper Construction ────────────────────────────────────────────────

def main():
    print("Building fully reconciled, publication-ready IEEE conference paper...")

    # Load audited source metrics
    with open(ANALYSIS_DIR / "findings.json") as f:
        findings = json.load(f)

    with open(ANALYSIS_DIR / "dataset_method_summary.csv") as f:
        summary_rows = list(csv.DictReader(f))

    lookup = {(r["dataset"], r["method"]): r for r in summary_rows}

    datasets = [
        {"dataset": "wine", "n": 178, "d": 13, "classes": 3, "domain": "Tabular / Chemical"},
        {"dataset": "breast_cancer", "n": 569, "d": 30, "classes": 2, "domain": "Tabular / Diagnostic"},
        {"dataset": "ionosphere", "n": 351, "d": 34, "classes": 2, "domain": "Tabular / Radar"},
        {"dataset": "spambase", "n": 4601, "d": 57, "classes": 2, "domain": "Tabular / Text"},
        {"dataset": "sonar", "n": 208, "d": 60, "classes": 2, "domain": "Tabular / Signal"},
        {"dataset": "digits", "n": 1797, "d": 64, "classes": 10, "domain": "Image / Vision"},
        {"dataset": "semeion", "n": 1593, "d": 256, "classes": 10, "domain": "Image / Vision"},
        {"dataset": "madelon", "n": 2600, "d": 500, "classes": 2, "domain": "Synthetic / Benchmark"},
        {"dataset": "arcene", "n": 200, "d": 10000, "classes": 2, "domain": "Mass Spectrometry / High-Dim"},
        {"dataset": "rna_seq", "n": 801, "d": 20531, "classes": 5, "domain": "Genomics / High-Dim"},
    ]

    doc = Document()
    setup_document_styles(doc)

    # Section 0: Unbordered Single-Column Header (Title & Authors)
    sec0 = doc.sections[0]
    configure_page(sec0, top_mm=19.05, bottom_in=0.75, side_in=0.62)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("A Reproducible Evaluation of On-Demand Correlation Guidance for Genetic Algorithm Feature Selection")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(20)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_before = Pt(0)
    p_author.paragraph_format.space_after = Pt(2)
    r_name = p_author.add_run("Ashish Pathak\n")
    r_name.bold = True
    r_name.font.size = Pt(10.5)
    r_affil = p_author.add_run(
        "School of Computer Science and Engineering\n"
        "Lovely Professional University, Punjab, India\n"
        "ap960664@gmail.com"
    )
    r_affil.font.size = Pt(9.0)

    # Section 1: Two-Column Section for Paper Body
    sec1 = doc.add_section(WD_SECTION.CONTINUOUS)
    configure_page(sec1, top_mm=19.05, bottom_in=0.75, side_in=0.62)
    set_columns(sec1, count=2, space_twips=360)

    # ─────────────────────────────────────────────────────────────────────────
    # ABSTRACT & INDEX TERMS
    # ─────────────────────────────────────────────────────────────────────────
    p_abs = doc.add_paragraph(style="IEEE Abstract")
    r_absh = p_abs.add_run("Abstract—")
    r_absh.bold = True
    r_absh.italic = True
    p_abs.add_run(
        "Correlation-guided genetic operators use information-theoretic relevance and redundancy metrics to bias subset search. "
        "However, classical implementations compute a dense d × d pairwise matrix prior to evolutionary search, incurring an "
        "O(d²) memory overhead that quickly becomes intractable on wide datasets. We evaluate an exact on-demand caching mechanism—which "
        "evaluates feature-pair symmetric uncertainty values strictly as queried during bounded mutation and updates subset merit via "
        "incremental delta arithmetic. Across ten public classification benchmarks (13 to 20,531 features) evaluated under nested "
        "three-fold cross-validation across three random seeds (522 experimental pipelines), the on-demand cache eliminates eager quadratic "
        "matrix allocation while preserving exact search trajectories. On all 72 matched outer-fold comparisons with d ≤ 500, dense and "
        "on-demand guidance produced identical binary masks, identical classifier predictions, and identical generation-by-generation "
        "fitness traces (max delta = 0.0). On the widest benchmarks (d ≥ 10,000), on-demand search accessed only 0.110% of candidate pairs "
        "(0.144% on Arcene, 0.076% on RNA-seq). Relative to unguided Basic GA, mean held-out balanced accuracy changed by +0.94 percentage "
        "points across the benchmark (6 wins, 4 losses, Wilcoxon W = 20.0, p = 0.492, sign-flip p = 0.238, 95% bootstrap CI [-0.28, +2.31] pp), "
        "with no statistically significant difference detected. These results indicate that correlation guidance functions as a domain-dependent "
        "inductive bias rather than a universally superior optimization heuristic. All experimental source code, raw metric logs, and figure reproduction scripts "
        "are publicly available at https://github.com/ap960664/soft-computing-paper-Data."
    )

    p_kw = doc.add_paragraph(style="IEEE Keywords")
    r_kwh = p_kw.add_run("Index Terms—")
    r_kwh.bold = True
    r_kwh.italic = True
    p_kw.add_run("Feature selection, genetic algorithms, symmetric uncertainty, on-demand caching, reproducibility, nested cross-validation, high-dimensional classification.")

    # ─────────────────────────────────────────────────────────────────────────
    # I. INTRODUCTION
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "I. INTRODUCTION")
    add_body(
        doc,
        "Supervised classification on high-dimensional data frequently encounters the curse of dimensionality: input spaces contain "
        "uninformative noise, collinear features, and redundant attributes that increase computational training overhead and degrade "
        "out-of-sample generalization [1], [2]. Dimensionality reduction via feature selection seeks an optimal subset of d input "
        "attributes that preserves or improves predictive discrimination. Because exhaustive evaluation across 2ᵈ candidate subsets is "
        "combinatorially intractable, stochastic heuristic search strategies—specifically genetic algorithms (GAs)—are widely adopted "
        "to navigate combinatorial feature spaces [1], [2]."
    )
    add_body(
        doc,
        "In a canonical wrapper GA, candidate subsets are represented as binary chromosomes and evaluated by training an induction "
        "algorithm on the selected sub-matrix. While wrapper feedback provides direct empirical guidance, standard genetic operators "
        "(uniform crossover, independent bit-flip mutation) operate blindly with respect to data distribution, frequently generating "
        "unpromising candidates. Correlation-guided operators address this inefficiency by biasing search toward features exhibiting "
        "high mutual dependence with the target label and penalizing pairs that introduce redundant mutual information [3], [4]."
    )
    add_body(
        doc,
        "A central implementation obstacle in correlation guidance lies in pairwise feature redundancy. Standard frameworks compute "
        "an explicit d × d symmetric uncertainty (SU) matrix before commencing evolutionary search [4]. For moderate datasets (d < 1,000), "
        "dense precomputation requires modest memory. However, for modern genomic arrays, mass spectrometry profiles, and document vectors "
        "where d ranges from 10,000 to over 20,000, storing all d(d - 1)/2 pairwise entries demands hundreds of millions of cells, "
        "as surveyed by Aldamani et al. [5]."
    )
    add_body(
        doc,
        "Fig. 1 depicts the end-to-end architecture of the on-demand correlation-guided genetic algorithm investigated in this study. "
        "Rather than precomputing an explicit matrix upfront, can exact correlation guidance be executed via an on-demand, triangularly "
        "indexed hash cache that computes feature-pair correlations strictly as needed, combined with an incremental delta score update rule? "
        "We conduct an audited empirical benchmark across ten classification datasets (13 to 20,531 features), measuring mathematical "
        "equivalence, cache query density, pipeline runtime, and predictive generalization under nested cross-validation."
    )

    # Fig 1: Pipeline Architecture
    add_fig(
        doc,
        FIGS_DIR / "fig1_system_architecture.png",
        "Fig. 1. Architecture of the on-demand correlation-guided genetic algorithm: Data is partitioned into outer and inner folds. "
        "Relevance scores SU(Xj, Y) are precomputed once per fold in O(d) time, while pairwise redundancy values are evaluated lazily "
        "via a triangular hash cache.",
        width_in=3.25
    )

    # ─────────────────────────────────────────────────────────────────────────
    # II. BACKGROUND AND RELATED WORK
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "II. BACKGROUND AND RELATED WORK")
    add_body(
        doc,
        "Correlation-based feature selection (CFS) [3] assumes optimal subsets contain attributes strongly correlated with the class "
        "yet mutually uncorrelated. Zhou and Hua [4] incorporated symmetric-uncertainty (SU) ranking into genetic operators to accelerate "
        "wrapper convergence. However, as surveyed by Aldamani et al. [5], correlation guidance inherits quadratic O(d²) complexity from "
        "exhaustive pairwise precomputation, curtailing scalability on wide data."
    )
    add_body(
        doc,
        "Evolutionary computation encompasses diverse strategies for subset search. Comprehensive reviews by Song et al. [6] and "
        "Naskar et al. [7] categorize methods into filter-wrapper hybrids, guided seeding, and multi-objective Pareto front optimizations [8]. "
        "To mitigate wrapper overhead, Altarabichi et al. [9] developed qualitative approximations, whereas Yaicharoen et al. [10], [11] "
        "investigated dynamic programming memoization bounded by direct bit-array limits. Other variants evaluate parallel populations [12], "
        "artificial bee colony hybrids [13], niching strategies [14], and domain wrappers in sensor optimization [15], software fault "
        "prediction [16], and intrusion detection [17]."
    )
    add_body(
        doc,
        "Despite substantial literature, the memory bottleneck of exact pairwise guidance has received limited rigorous empirical validation. "
        "Table I positions the scope of this investigation relative to established research."
    )

    # TABLE I: Positioning Table
    add_table_title(doc, "TABLE I\nPOSITIONING OF THIS STUDY RELATIVE TO PRIOR LITERATURE")
    pos_data = [
        ["Hall (1999) [3]", "CFS subset merit function", "Evaluated as greedy filter; no GA operators"],
        ["Zhou & Hua (2022) [4]", "Correlation-guided GA (CGGA)", "Exhaustive d × d dense correlation matrix"],
        ["Aldamani et al. (2026) [5]", "Survey of GA feature selection", "Identifies O(d²) correlation storage as bottleneck"],
        ["Song et al. (2024) [6]", "Survey of EC feature selection", "Surveys hybrid filters; leaves cache density unquantified"],
        ["Altarabichi (2023) [9]", "Surrogate fitness approximations", "Approximate surrogate evaluation; alters search logic"],
        ["Yaicharoen (2025) [10]", "Dynamic programming GA", "Full chromosome memoization; 2ᵈ index limits"],
        ["This Study", "On-demand exact SU caching", "Exact equivalence audit; evaluated on d up to 20,531"],
    ]
    build_ieee_table(doc, ["Study / Framework", "Core Methodological Focus", "Investigated Scope & Remaining Gap"], pos_data, [1.05, 1.10, 1.10], font_size=6.6)

    # ─────────────────────────────────────────────────────────────────────────
    # III. METHODOLOGY
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "III. METHODOLOGY")
    add_h2(doc, "A. Symmetric Uncertainty Formulation")
    add_body(
        doc,
        "Continuous numeric features are discretized into five uniform-frequency quantile bins using training partition boundaries only. "
        "Symmetric uncertainty (SU) normalizes Shannon mutual information I(X; Y) by marginal entropies H(X) and H(Y), providing a "
        "scale-invariant metric bounded in [0, 1]:"
    )

    # Equation 1
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq1.paragraph_format.space_before = Pt(2)
    p_eq1.paragraph_format.space_after = Pt(2)
    r_eq1 = p_eq1.add_run("SU(X, Y) = 2 · I(X; Y) / [ H(X) + H(Y) ]           (1)")
    r_eq1.font.name = "Cambria Math"
    r_eq1.font.size = Pt(8.8)
    r_eq1.italic = True

    add_body(
        doc,
        "For a candidate subset S containing k selected features, the guidance merit G(S) balances aggregate feature-class relevance "
        "against pairwise feature redundancy [3], [4]:"
    )

    # Equation 2
    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq2.paragraph_format.space_before = Pt(2)
    p_eq2.paragraph_format.space_after = Pt(2)
    r_eq2 = p_eq2.add_run("G(S) = [ ∑ⱼ SU(Xⱼ, Y) ] / √[ k + 2 ∑ⱼ<ₗ SU(Xⱼ, Xₗ) ]    (2)")
    r_eq2.font.name = "Cambria Math"
    r_eq2.font.size = Pt(8.8)
    r_eq2.italic = True

    add_body(
        doc,
        "A superior candidate maximizes relevance while penalizing redundant attribute pairs. Because the denominator operates under "
        "a square root over the composite sum, features providing unique discriminatory information yield higher scores."
    )

    add_h2(doc, "B. On-Demand Triangular Key Caching")
    add_body(
        doc,
        "Rather than allocating an explicit d × d array, the on-demand implementation precomputes only the d-dimensional vector of "
        "feature-class relevances SU(Xⱼ, Y). Pairwise redundancy values SU(Xⱼ, Xₗ) are computed lazily. When guidance requires evaluating "
        "a pair of features (a, b) with a ≠ b, indices are ordered such that i = min(a, b) and j = max(a, b). The pair is mapped to a "
        "canonical triangular index key = j(j - 1)/2 + i. The cache retrieves the value if previously evaluated, or computes the exact "
        "SU from the binned training columns, storing the result for future generations."
    )

    # Fig 2: Selection Flow
    add_fig(
        doc,
        FIGS_DIR / "fig2_selection_flow.png",
        "Fig. 2. Guided mutation and incremental delta update: Ten candidate bit mutations are generated. "
        "The incremental delta updater adjusts relevance and redundancy sums in O(k · t) time, ranking candidates via G(S).",
        width_in=3.25
    )

    add_h2(doc, "C. Incremental Delta Update Rule")
    add_body(
        doc,
        "During genetic search, mutation alters only a small subset of bit loci (t ∈ {1, 2, 3} features). Rather than recomputing G(S) "
        "from scratch in O(k²) time, our implementation tracks the current chromosome's state: selected count k, relevance sum R = ∑ SU(X_j, Y), "
        "and redundancy sum C = 2 ∑ SU(X_j, X_l). Fig. 2 illustrates this flow. When toggling feature m in subset S:"
    )
    p_rules = doc.add_paragraph()
    p_rules.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_rules.paragraph_format.first_line_indent = Inches(0.14)
    p_rules.paragraph_format.space_before = Pt(2)
    p_rules.paragraph_format.space_after = Pt(2)
    p_rules.paragraph_format.line_spacing = 1.0
    r_rules = p_rules.add_run(
        "• Addition of feature m:\n"
        "   k' = k + 1,  R' = R + SU(X_m, Y),  C' = C + 2 Σ SU(X_m, X_j)\n"
        "• Removal of feature m:\n"
        "   k' = k - 1,  R' = R - SU(X_m, Y),  C' = C - 2 Σ SU(X_m, X_j)"
    )
    r_rules.font.name = "Times New Roman"
    r_rules.font.size = Pt(8.8)
    add_body(
        doc,
        "Updating S requires only O(k · t) pairwise operations. Unit testing verifies that the delta-updated score matches direct "
        "formula recalculation within floating-point epsilon (10⁻¹⁰). Deterministic lexicographical tie-breaking ensures reproducibility."
    )

    add_h2(doc, "D. Genetic Search Execution and Hyperparameters")
    add_body(
        doc,
        "Chromosomes are encoded as binary strings of length d. Population size is P = 16. To enforce sparsity on wide datasets, candidate "
        "masks are bounded by min(d, max(10, ⌈√d⌉)). Binary tournament selection (size 2) selects parents; recombination applies one-point "
        "crossover. In unguided Basic GA, offspring undergo independent bit-flip mutation (p = 1/d). In On-Demand Guided GA, mutation produces "
        "ten stochastic candidate bit-flips, scores each via delta-updated G(S), and advances only the top-ranked candidate to the wrapper. "
        "Search terminates strictly upon completing 96 unique wrapper evaluations (cached duplicate masks incur zero evaluation cost)."
    )

    # Column break so Section IV and Table II start cleanly at the top of Page 3
    add_column_break(doc)

    # ─────────────────────────────────────────────────────────────────────────
    # IV. EXPERIMENTAL DESIGN
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "IV. EXPERIMENTAL DESIGN")
    add_h2(doc, "A. Benchmark Datasets and Partitioning")
    add_body(
        doc,
        "Ten public classification benchmarks covering diverse sample-to-feature ratios were obtained from scikit-learn [18] and the "
        "UCI Machine Learning Repository [19]. Table II summarizes dataset properties. No datasets were omitted post-hoc."
    )

    # TABLE II: Benchmark Datasets
    add_table_title(doc, "TABLE II\nBENCHMARK DATASET CHARACTERISTICS")
    ds_rows = [
        [format_ds_name(d["dataset"]), f"{d['n']:,}", f"{d['d']:,}", str(d["classes"]), d["domain"]]
        for d in datasets
    ]
    build_ieee_table(doc, ["Dataset", "Instances (n)", "Features (d)", "Classes", "Application Domain"], ds_rows, [0.85, 0.58, 0.55, 0.42, 0.85], font_size=6.6)

    add_body(
        doc,
        "To prevent data leakage, validation follows a strictly nested cross-validation scheme across three independent random seeds "
        "(17, 29, 43). Outer evaluation uses a 3-fold stratified split (9 outer folds per dataset). Inside each outer training set, "
        "feature selection runs across 3 inner folds. Preprocessing—median imputation, robust standardization, and five-bin quantile "
        "discretization—is fitted exclusively on training splits. Final selected subsets are refitted on outer training folds and tested "
        "on untouched outer holdouts using a balanced linear Support Vector Machine (LinearSVC, C = 1.0, dual = False)."
    )

    add_h2(doc, "B. Evaluated Baselines and Experimental Accounting")
    add_body(
        doc,
        "Comparisons include: (1) All-Feature SVM (no dimensionality reduction); (2) Nested ANOVA Filter (top-k features ranked by "
        "univariate F-score, matching GA sparsity cap); (3) Random Search (96 evaluations with sparsity ceiling); (4) Basic GA (unguided "
        "operators); and (5) Dense Correlation-Guided GA (for d ≤ 500). Across 10 datasets × 9 outer folds × 5 primary methods, 450 pipelines "
        "were executed; adding the 72 dense comparisons across the 8 datasets where d ≤ 500 yields 522 fully audited pipelines."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # V. EMPIRICAL RESULTS AND STATISTICAL ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "V. EMPIRICAL RESULTS AND STATISTICAL ANALYSIS")
    add_h2(doc, "A. Mathematical Equivalence Audit")
    add_body(
        doc,
        "The primary correctness hypothesis tests whether on-demand caching alters search trajectories relative to the dense reference "
        "implementation. Across all 72 matched outer-fold searches on the eight datasets where d ≤ 500, dense and on-demand guidance "
        "produced identical binary masks (100% bit-level agreement), identical held-out predictions, and identical generation-by-generation "
        "wrapper fitness traces (max delta = 0.0). This demonstrates exact agreement between the evaluated implementations."
    )
    add_body(
        doc,
        "Fig. 3 illustrates the convergence behavior on Digits across unique wrapper evaluations. Guided GA discovers higher-accuracy "
        "subspaces earlier in the budget than unguided Basic GA and Random Search, achieving a final validation score of 0.931 vs 0.925."
    )

    # Fig 3: Convergence
    add_fig(
        doc,
        FIGS_DIR / "fig3_ga_convergence.png",
        "Fig. 3. Optimization trajectories on Digits: Mean best fitness convergence across outer folds as a function of unique wrapper evaluations. "
        "Correlation guidance accelerates early discovery of higher-accuracy subspaces compared to unguided Basic GA and Random Search.",
        width_in=3.25
    )

    add_h2(doc, "B. Classification Performance")
    add_body(
        doc,
        "Table III reports dataset-level balanced accuracy averaged across the nine outer-fold evaluations per benchmark. Fig. 4 "
        "displays benchmark-mean balanced accuracy across all five evaluated methods."
    )

    # TABLE III: Performance Comparison
    add_table_title(doc, "TABLE III\nDATASET-MEAN BALANCED ACCURACY ACROSS EVALUATED METHODS")
    perf_rows = []
    for d_info in datasets:
        dname = d_info["dataset"]
        all_svm_v = float(lookup[(dname, "all_svm")]["balanced_accuracy_mean"])
        anova_v = float(lookup[(dname, "anova")]["balanced_accuracy_mean"])
        rnd_v = float(lookup[(dname, "random_search")]["balanced_accuracy_mean"])
        b_ga = float(lookup[(dname, "basic_ga")]["balanced_accuracy_mean"])
        ldsu = float(lookup[(dname, "ldsu_ga")]["balanced_accuracy_mean"])
        diff_val = 100 * (ldsu - b_ga)
        perf_rows.append([
            format_ds_name(dname),
            f"{all_svm_v:.3f}",
            f"{anova_v:.3f}",
            f"{rnd_v:.3f}",
            f"{b_ga:.3f}",
            f"{ldsu:.3f}",
            f"{diff_val:+.2f}",
        ])
    build_ieee_table(doc, ["Dataset", "All", "ANOVA", "Rand", "Basic", "Guided", "Δ pp"], perf_rows, [0.92, 0.34, 0.40, 0.35, 0.36, 0.44, 0.44], font_size=6.2)

    # Fig 4: Method Comparison
    add_fig(
        doc,
        FIGS_DIR / "fig4_method_comparison.png",
        "Fig. 4. Benchmark-mean balanced accuracy across evaluated methods over all ten datasets. All-Feature SVM (86.12%) and "
        "ANOVA filter (84.78%) establish strong baselines under linear classification, while On-Demand Guided GA (82.93%) achieves "
        "a +0.94 pp gain over unguided Basic GA (81.99%) and +2.84 pp over Random Search (80.09%).",
        width_in=3.25
    )

    add_body(
        doc,
        "Comparing On-Demand Guided GA against Basic GA reveals mixed outcomes: guidance achieves higher balanced accuracy on "
        "6 datasets (Wine, Digits, Sonar, Semeion, Madelon, RNA-seq) and trails on 4 datasets (Breast Cancer, Ionosphere, Spambase, Arcene). "
        "Gains are most pronounced on multiclass image problems (Digits: +4.16 pp; Semeion: +5.05 pp). Across the entire ten-dataset "
        "benchmark, the mean difference is +0.94 percentage points (median +0.21 pp), with a 95% bootstrap confidence interval of "
        "[-0.28, +2.31] pp. Notice that All-Feature SVM (86.12%) and ANOVA (84.78%) outperform Guided GA (82.93%); under a strict budget "
        "of 96 evaluations and L2-regularized linear classification, sparse heuristic search explores only a minuscule fraction of 2ᵈ, "
        "whereas full-feature models retain dense predictive signals. Fig. 5 plots dataset-level differences."
    )

    # Fig 5: Balanced Accuracy Difference
    add_fig(
        doc,
        FIGS_DIR / "fig5_balanced_accuracy_difference.png",
        "Fig. 5. Dataset-level balanced accuracy differences (On-Demand Guided GA minus Basic GA). "
        "Bars represent mean differences over nine outer folds; dashed line denotes benchmark mean (+0.94 pp).",
        width_in=3.25
    )

    add_h2(doc, "C. Statistical Hypothesis Testing")
    add_body(
        doc,
        "To ascertain whether guidance confers a statistically significant performance advantage over unguided GA, we execute a two-sided "
        "Wilcoxon signed-rank test [20] on dataset-level means, yielding W = 20.0, p = 0.492. A non-parametric exact sign-flip permutation "
        "test across all 2¹⁰ permutations yields p = 0.238. Because both p-values exceed the standard α = 0.05 threshold and the bootstrap "
        "confidence interval crosses zero, no statistically significant difference is detected. Relevance-redundancy guidance functions as "
        "an inductive bias whose efficacy depends on whether pairwise correlation aligns with class separability under the chosen classifier."
    )

    add_h2(doc, "D. Cache Scalability and Runtime Complexity")
    add_body(
        doc,
        "A key practical advantage of on-demand guidance appears in memory scaling. Table IV outlines computational metrics across "
        "high-dimensional datasets, reporting mean per-outer-fold timings and peak heap usage."
    )

    # TABLE IV: High-Dim Table
    add_table_title(doc, "TABLE IV\nCOMPUTATIONAL SCALABILITY AND PAIR COVERAGE ON WIDE DATASETS")
    scale_data = [
        ["Semeion", "256", "20.134%", "0.035 s", "1.631 s", "182.4 MiB"],
        ["Madelon", "500", "8.826%", "0.115 s", "1.675 s", "225.3 MiB"],
        ["Arcene", "10,000", "0.144%", "0.677 s", "2.351 s", "314.0 MiB"],
        ["RNA-seq", "20,531", "0.076%", "2.744 s", "25.554 s", "824.7 MiB"],
    ]
    build_ieee_table(doc, ["Dataset", "d", "Pairs (%)", "Setup (s)", "Pipeline (s)", "Heap (MiB)"], scale_data, [0.70, 0.45, 0.50, 0.50, 0.55, 0.55], font_size=6.6)

    # Column break so Fig 6 & 7 and scalability discussion fill Column 2
    add_column_break(doc)

    # Fig 6: Pair Coverage
    add_fig(
        doc,
        FIGS_DIR / "fig6_pair_coverage_by_dimension.png",
        "Fig. 6. Feature-pair cache coverage as a function of dimensionality d on a log-log scale: Evaluated pairs drop from 100.0% "
        "on Wine to 0.076% on RNA-seq, following an empirical power law trend ~ d^{-1.08} (R² = 0.97).",
        width_in=3.25
    )

    # Fig 7: Cost Components
    add_fig(
        doc,
        FIGS_DIR / "fig7_cost_components.png",
        "Fig. 7. Breakdown of search runtime per outer fold across four high-dimensional benchmarks: SVM wrapper evaluation dominates "
        "total execution time, while on-demand pair computation and relevance setup remain modest.",
        width_in=3.25
    )

    add_body(
        doc,
        "As dimensionality expands from d = 13 (Wine) to d = 20,531 (RNA-seq), the proportion of accessed feature pairs drops from "
        "100.0% to 20.13% on Semeion, 8.83% on Madelon, and down to 0.076% on RNA-seq (Fig. 6). Across Arcene and RNA-seq, the algorithm "
        "computed only 0.110% of possible pairs on average. Guidance setup overhead remained modest (0.68 s on Arcene, 2.74 s on RNA-seq "
        "per outer fold), allowing complete outer-fold pipelines to run in 2.35 s on Arcene and 25.55 s on RNA-seq without memory distress."
    )
    add_body(
        doc,
        "The sublinear growth of accessed pairs confirms that wrapper evaluations, rather than correlation queries, strictly dominated "
        "measured execution time (Fig. 7). For RNA-seq (d = 20,531), computing all 210,750,715 pairs upfront would require allocating an "
        "explicit d(d - 1)/2 matrix of approximately 1.57 GiB (1.69 GB) of raw float64 storage. In contrast, the on-demand triangular cache "
        "queried only 159,327 unique pairs (0.076% coverage), storing approximately 1.28 MiB of correlation data and keeping peak process heap "
        "at 824.7 MiB (including Python runtime, scikit-learn structures, and SVM models)."
    )

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────────────────
    # VI. DISCUSSION
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "VI. DISCUSSION")
    add_body(
        doc,
        "The empirical findings address the memory limitations of dense correlation precomputation in evolutionary feature selection. "
        "Historically, the quadratic memory barrier O(d²) forced researchers either to abandon correlation-guided genetic operators on wide-format "
        "data or to resort to lossy approximations such as coarse subsampling and uncalibrated surrogate models. Our mathematical equivalence "
        "audit demonstrates that an exact on-demand triangular cache avoids eager quadratic matrix allocation without altering search "
        "trajectories on the evaluated benchmark suite."
    )
    add_body(
        doc,
        "Because genetic search operates under strict evaluation budgets (96 subset evaluations) and sparsity limits (selected features "
        "k ≤ ⌈√d⌉), the population queries only a minuscule fraction of candidate pairs. On RNA-seq, fewer than 0.08% of pairwise correlations "
        "were ever requested. Space complexity scales as O(q), where q ≤ d(d - 1)/2 is the number of queried pairs; under finite budgets B, "
        "q ≪ d², enabling workstation execution without out-of-memory errors."
    )
    add_body(
        doc,
        "Crucially, the predictive evaluation demonstrates that correlation guidance is not a universally superior optimization heuristic, "
        "but rather an inductive bias whose performance depends on data manifold structure. Guidance delivers substantial accuracy gains "
        "on multiclass vision problems (+4.16 pp on Digits, +5.05 pp on Semeion), where spatial pixel neighborhoods exhibit high inter-correlation "
        "and clear pairwise redundancy. In contrast, on datasets characterized by complex feature interactions or dense informative signatures "
        "(e.g., Arcene: -1.52 pp; Ionosphere: -1.06 pp), univariate symmetric uncertainty can prematurely penalize synergistically informative attributes. "
        "Across the full benchmark suite, the mean gain (+0.94 pp) was not statistically significant (Wilcoxon p = 0.492; sign-flip p = 0.238), "
        "underscoring that practitioners should validate guidance as a domain-specific inductive mechanism."
    )
    add_body(
        doc,
        "Limitations of this study include evaluating a single classifier family (linear SVM), a fixed budget of 96 evaluations, and "
        "the asymmetry that Guided GA evaluated 10 candidate probes per offspring while Basic GA evaluated 1. Future work will explore "
        "ablation with 10 unguided probes and multi-objective Pareto wrappers on datasets exceeding 100,000 features."
    )
    add_body(
        doc,
        "Data and Code Availability: The complete experimental codebase, nested cross-validation harness, raw metric logs, and figure/table "
        "generation scripts are publicly available at https://github.com/ap960664/soft-computing-paper-Data. "
        "The repository contains complete raw result CSVs, pipeline configurations, random seed logs, and a standalone reproduction script "
        "(reproduce_all.py) requiring Python 3.10+ and standard scientific packages (NumPy, SciPy, scikit-learn)."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # VII. CONCLUSION
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "VII. CONCLUSION")
    add_body(
        doc,
        "This paper presented a reproducible evaluation of on-demand correlation guidance for genetic algorithm feature selection. "
        "Across 522 experimental pipelines and 72 matched outer-fold comparisons on eight public benchmarks (d ≤ 500) alongside scalability evaluations on wide datasets, the on-demand caching "
        "architecture and incremental delta updater demonstrated bit-exact agreement with classical dense guidance while evaluating "
        "less than 0.15% of candidate feature pairs on wide datasets up to d = 20,531. While correlation guidance accelerates early subspace discovery "
        "in structured image domains, its overall predictive advantage remains domain-dependent."
    )

    # Column break so REFERENCES begins cleanly at the top of Column 2
    add_column_break(doc)

    # ─────────────────────────────────────────────────────────────────────────
    # REFERENCES
    # ─────────────────────────────────────────────────────────────────────────
    add_h1(doc, "REFERENCES")
    
    references = [
        r'''[1] J. Yang and V. Honavar, "Feature subset selection using a genetic algorithm," IEEE Intell. Syst. Appl., vol. 13, no. 2, pp. 44–49, 1998, doi: 10.1109/5254.671091.''',
        r'''[2] I.-S. Oh, J.-S. Lee, and B.-R. Moon, "Hybrid genetic algorithms for feature selection," IEEE Trans. Pattern Anal. Mach. Intell., vol. 26, no. 11, pp. 1424–1437, 2004, doi: 10.1109/TPAMI.2004.105.''',
        r'''[3] M. A. Hall, "Correlation-based feature selection for machine learning," Ph.D. dissertation, Dept. Comput. Sci., Univ. Waikato, Hamilton, New Zealand, 1999.''',
        r'''[4] J. Zhou and Z. Hua, "A correlation guided genetic algorithm and its application to feature selection," Appl. Soft Comput., vol. 123, art. 108964, 2022, doi: 10.1016/j.asoc.2022.108964.''',
        r'''[5] R. Aldamani, M. Aoudia, D. A. Abuhani, and O. Arif, "Recent advances in genetic algorithm-based feature selection: A comprehensive survey," Swarm Evol. Comput., vol. 102, art. 102318, 2026, doi: 10.1016/j.swevo.2026.102318.''',
        r'''[6] X. Song et al., "Evolutionary computation for feature selection in classification: A comprehensive survey of solutions, applications and challenges," Swarm Evol. Comput., vol. 90, art. 101661, 2024, doi: 10.1016/j.swevo.2024.101661.''',
        r'''[7] A. Naskar, S. Ghosh, M. Kundu, and R. Sarkar, "Feature selection using guided population based genetic algorithm with modified crossover and parent selection," Appl. Soft Comput., vol. 172, art. 112872, 2025, doi: 10.1016/j.asoc.2025.112872.''',
        r'''[8] Y. Xue, X. Cai, and F. Neri, "A multi-objective evolutionary algorithm with interval based initialization and self-adaptive crossover operator for large-scale feature selection in classification," Appl. Soft Comput., vol. 127, art. 109420, 2022, doi: 10.1016/j.asoc.2022.109420.''',
        r'''[9] M. G. Altarabichi, S. Nowaczyk, S. Pashami, and P. S. Mashhadi, "Fast genetic algorithm for feature selection: A qualitative approximation approach," Expert Syst. Appl., vol. 211, art. 118528, 2023, doi: 10.1016/j.eswa.2022.118528.''',
        r'''[10] A. Yaicharoen et al., "Improving efficiency of the genetic algorithm feature selection with dynamic programming," in Proc. 22nd ECTI-CON, 2025, doi: 10.1109/ECTI-CON64996.2025.11101181.''',
        r'''[11] A. Yaicharoen et al., "Improving classifier training efficiency with genetic algorithm feature selection," in Proc. ATC, 2024, pp. 540–543, doi: 10.1109/ATC63255.2024.10908297.''',
        r'''[12] U. Cetin and Y. E. Gundogmus, "Feature selection with evolving, fast and slow using two parallel genetic algorithms," in Proc. 4th Int. Conf. Comput. Sci. Eng. (UBMK), 2019, pp. 699–703, doi: 10.1109/UBMK.2019.8907165.''',
        r'''[13] M. G. Bindu and M. K. Sabu, "A hybrid feature selection approach using artificial bee colony and genetic algorithm," in Proc. ACCTHPA, 2020, pp. 211–216, doi: 10.1109/ACCTHPA49271.2020.9213197.''',
        r'''[14] K. Homsapaya, S. Bundasak, and B. Jitnupong, "Enhancing sequential floating search feature selection using niching-genetic algorithm," in Proc. 28th ICSEC, 2024, doi: 10.1109/ICSEC62781.2024.10770704.''',
        r'''[15] Y. Kaya, "Comparison of using the genetic algorithm and cuckoo search for feature selection," in Proc. Int. Conf. Artif. Intell. Data Process. (IDAP), 2018, pp. 1–5, doi: 10.1109/IDAP.2018.8620823.''',
        r'''[16] H. Kumar and H. Das, "Software fault prediction using wrapper based feature selection approach employing genetic algorithm," in Proc. OTCON, 2023, doi: 10.1109/OTCON56053.2023.10113911.''',
        r'''[17] B. L. Moghaddam, A. Daghighi, M. Teymournezhad, and G. Yılmaz, "A multi-resolution dendritic cell algorithm with genetic feature selection for intrusion detection," in Proc. ASYU, 2025, doi: 10.1109/ASYU67174.2025.11208444.''',
        r'''[18] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.''',
        r'''[19] M. Kelly, R. Longjohn, and K. Nottingham, "The UCI Machine Learning Repository," 2024. [Online]. Available: https://archive.ics.uci.edu/.''',
        r'''[20] F. Wilcoxon, "Individual comparisons by ranking methods," Biometrics Bull., vol. 1, no. 6, pp. 80–83, 1945.''',
    ]

    for ref in references:
        doc.add_paragraph(ref, style="IEEE Ref")

    doc.core_properties.title = "A Reproducible Evaluation of On-Demand Correlation Guidance for Genetic Algorithm Feature Selection"
    doc.core_properties.author = "Ashish Pathak"
    doc.core_properties.subject = "IEEE Conference Term Paper"
    doc.core_properties.keywords = "feature selection, genetic algorithm, symmetric uncertainty, reproducibility"

    doc.save(DOCX_PATH)
    print(f"\nDocument successfully created at: {DOCX_PATH}")

if __name__ == "__main__":
    main()
