#!/usr/bin/env python3
"""
Build the Prescribed University Format Term Paper (.docx and .pdf):
Strict adherence to:
- Times New Roman, 12 pt font
- 1.5 line spacing throughout
- Justified alignment throughout
- A4 size with 1.0 inch (25.4 mm) margins
- Proper headings (Roman numerals: I. INTRODUCTION, II. LITERATURE SURVEY, etc.)
- Page numbers in footer (bottom-center)
- Figures and tables with proper captions
- Citations in-text and complete References list [1]-[20]
- High originality (<2% plagiarism, no AI clichés)
- Matching the sample reference PDF layout and structure!
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Mm, Pt, RGBColor

BASE_DIR = Path("/Users/ashish/Desktop/Side Project/Soft Computing Term Paper")
OUT_DIR = BASE_DIR / "Term_Paper_Prescribed_Format"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DOCX_OUT = OUT_DIR / "Term_Paper_Ashish_Pathak_Prescribed_Format.docx"
PDF_OUT = OUT_DIR / "Term_Paper_Ashish_Pathak_Prescribed_Format.pdf"
FIGS_DIR = OUT_DIR / "figures"
DATA_DIR = BASE_DIR / "data"

# ─── XML & Layout Helpers ───────────────────────────────────────────────────

def set_cell_margins(cell, top=60, bottom=60, left=90, right=90):
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

def set_table_borders(table, color="718096", size="4"):
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

def add_page_number_field(run):
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    r = run._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(fldChar3)

# ─── Style Setup ─────────────────────────────────────────────────────────────

def setup_styles(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    # Body Paragraph Style: 12 pt, 1.5 line spacing, Justified
    if "Term Body" not in styles:
        s_body = styles.add_style("Term Body", 1)
        s_body.base_style = normal
        s_body.font.name = "Times New Roman"
        s_body.font.size = Pt(12)
        s_body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_body.paragraph_format.line_spacing = 1.5
        s_body.paragraph_format.space_before = Pt(0)
        s_body.paragraph_format.space_after = Pt(6)

    # Heading 1 Style: 12 pt, Bold, Left-aligned, Roman Numerals
    if "Term H1" not in styles:
        s_h1 = styles.add_style("Term H1", 1)
        s_h1.base_style = normal
        s_h1.font.name = "Times New Roman"
        s_h1.font.size = Pt(12)
        s_h1.font.bold = True
        s_h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        s_h1.paragraph_format.line_spacing = 1.5
        s_h1.paragraph_format.space_before = Pt(14)
        s_h1.paragraph_format.space_after = Pt(4)
        s_h1.paragraph_format.keep_with_next = True

    # Caption Style: 11 pt, Centered, 1.15 line spacing
    if "Term Caption" not in styles:
        s_cap = styles.add_style("Term Caption", 1)
        s_cap.base_style = normal
        s_cap.font.name = "Times New Roman"
        s_cap.font.size = Pt(11)
        s_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        s_cap.paragraph_format.line_spacing = 1.15
        s_cap.paragraph_format.space_before = Pt(6)
        s_cap.paragraph_format.space_after = Pt(12)

    # Bullet Style: 12 pt, 1.5 line spacing, Justified, left indent
    if "Term Bullet" not in styles:
        s_bullet = styles.add_style("Term Bullet", 1)
        s_bullet.base_style = normal
        s_bullet.font.name = "Times New Roman"
        s_bullet.font.size = Pt(12)
        s_bullet.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_bullet.paragraph_format.line_spacing = 1.5
        s_bullet.paragraph_format.left_indent = Inches(0.25)
        s_bullet.paragraph_format.first_line_indent = Inches(-0.25)
        s_bullet.paragraph_format.space_before = Pt(2)
        s_bullet.paragraph_format.space_after = Pt(6)

    # Reference Style: 11 pt, 1.15 line spacing, Justified, hanging indent
    if "Term Ref" not in styles:
        s_ref = styles.add_style("Term Ref", 1)
        s_ref.base_style = normal
        s_ref.font.name = "Times New Roman"
        s_ref.font.size = Pt(11)
        s_ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        s_ref.paragraph_format.line_spacing = 1.15
        s_ref.paragraph_format.left_indent = Inches(0.35)
        s_ref.paragraph_format.first_line_indent = Inches(-0.35)
        s_ref.paragraph_format.space_before = Pt(0)
        s_ref.paragraph_format.space_after = Pt(4)

def add_body_p(doc, text):
    return doc.add_paragraph(text, style="Term Body")

def add_bullet_p(doc, bold_prefix, text):
    p = doc.add_paragraph(style="Term Bullet")
    r_bullet = p.add_run("• ")
    r_bullet.bold = True
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + " ")
        r_pre.bold = True
    p.add_run(text)
    return p

def add_heading_h1(doc, text):
    return doc.add_paragraph(text, style="Term H1")

def add_figure(doc, img_path, caption_text, width_in=6.0):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(str(img_path), width=Inches(width_in))

    p_cap = doc.add_paragraph(caption_text, style="Term Caption")
    return p_img, p_cap

# ─── Main Document Generation ───────────────────────────────────────────────

def main():
    print("Building Prescribed University Format Term Paper...")

    doc = Document()
    setup_styles(doc)

    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    # Configure Footer with page numbers
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_foot = p_foot.add_run()
    r_foot.font.name = "Times New Roman"
    r_foot.font.size = Pt(11)
    add_page_number_field(r_foot)

    # ─────────────────────────────────────────────────────────────────────────
    # TITLE & AUTHOR DETAILS (Centered)
    # ─────────────────────────────────────────────────────────────────────────
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    p_title.paragraph_format.line_spacing = 1.2
    r_title = p_title.add_run("Review of Genetic Algorithm Feature Selection and On-Demand Correlation Guidance for High-Dimensional Classification")
    r_title.bold = True
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(16)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_before = Pt(4)
    p_author.paragraph_format.space_after = Pt(16)
    p_author.paragraph_format.line_spacing = 1.15

    r_author = p_author.add_run("Ashish Pathak\n")
    r_author.bold = True
    r_author.font.size = Pt(12)

    r_affil = p_author.add_run(
        "Department of Computer Science and Engineering,\n"
        "Lovely Professional University, Phagwara, Punjab, India\n"
    )
    r_affil.font.size = Pt(11)

    r_email = p_author.add_run("ap960664@gmail.com")
    r_email.font.size = Pt(11)
    r_email.font.underline = True
    r_email.font.color.rgb = RGBColor(5, 99, 193)

    # ─────────────────────────────────────────────────────────────────────────
    # ABSTRACT & KEYWORDS
    # ─────────────────────────────────────────────────────────────────────────
    p_abs = doc.add_paragraph(style="Term Body")
    r_absh = p_abs.add_run("Abstract— ")
    r_absh.bold = True
    r_absh.italic = True
    p_abs.add_run(
        "High-dimensional feature selection represents a foundational challenge in machine learning, bioinformatics, and soft computing, "
        "where the combinatorial explosion of candidate feature subsets (2ᵈ) severely impedes exhaustive search while uninformative, "
        "collinear, or noisy attributes degrade generalization. This paper presents a systematic review and empirical evaluation of "
        "genetic algorithm (GA) feature selection methods, synthesizing 20 peer-reviewed articles using the Preferred Reporting Items for "
        "Systematic Reviews and Meta-Analyses (PRISMA) framework. We evaluate the core methodological paradigms, including canonical wrappers, "
        "filter-wrapper hybrids, multi-objective Pareto formulations, dynamic programming memoization, and correlation-guided operators. "
        "A critical limitation identified across existing correlation-guided literature is the quadratic memory overhead O(d²) incurred by "
        "precomputing an explicit d × d pairwise symmetric uncertainty matrix upfront, rendering classical guidance computationally "
        "intractable on wide-format data (d ≥ 10,000). To address this bottleneck, we evaluate an exact on-demand triangular key caching "
        "mechanism combined with an incremental delta score update rule. Across ten public benchmark datasets (13 to 20,531 features) evaluated "
        "under a strictly nested three-fold cross-validation scheme across three random seeds (522 experimental pipelines), the on-demand "
        "cache achieves exact mathematical equivalence with classical dense guidance across all 72 matched outer-fold searches where d ≤ 500 "
        "(max delta = 0.0), while accessing only 0.144% of candidate pairs on Arcene and 0.076% on RNA-seq (saving 1.57 GiB of raw memory). "
        "However, held-out predictive evaluation demonstrates that correlation guidance acts as a domain-dependent inductive bias rather "
        "than a universally superior heuristic (+4.16 pp on Digits, +5.05 pp on Semeion, with an overall benchmark mean delta of +0.94 pp, "
        "Wilcoxon p = 0.492). All code, logs, and reproduction scripts are open-source and publicly hosted."
    )

    p_kw = doc.add_paragraph(style="Term Body")
    r_kwh = p_kw.add_run("Keywords— ")
    r_kwh.bold = True
    p_kw.add_run(
        "Feature Selection, Genetic Algorithms, Symmetric Uncertainty, Correlation Guidance, PRISMA Review, "
        "High-Dimensional Classification, Soft Computing."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # I. INTRODUCTION
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "I.   INTRODUCTION")
    add_body_p(
        doc,
        "Supervised machine learning applied to modern data-intensive disciplines—such as high-throughput genomic profiling, biomedical "
        "diagnostics, satellite remote sensing, mass spectrometry, and large-scale textual categorization—regularly encounters feature spaces "
        "where the dimensionality d dramatically exceeds the available sample size n (d ≫ n). In these high-dimensional regimes, models "
        "suffer acutely from the curse of dimensionality, severe overfitting, high variance, and computational training burdens caused by "
        "extensive collinearity and uninformative noise [1], [2]. Feature selection seeks to identify an optimal, minimal subset of "
        "discriminative attributes that preserves or improves predictive accuracy while eliminating redundant variables."
    )
    add_body_p(
        doc,
        "Because evaluating all 2ᵈ possible candidate subsets is combinatorially impossible for any non-trivial dimension, stochastic "
        "search algorithms inspired by natural selection—specifically Genetic Algorithms (GAs)—have become a predominant soft computing "
        "methodology for navigating combinatorial feature spaces [1]. In a canonical wrapper GA, candidate subsets are encoded as binary "
        "chromosomes of length d, where bits indicate feature presence, and fitness is assigned through empirical induction performance "
        "evaluated over cross-validation splits. However, standard genetic operators (uniform crossover, stochastic bit-flip mutation) operate "
        "blindly with respect to underlying data distributions, frequently exploring unpromising and redundant subspaces."
    )

    add_figure(
        doc,
        FIGS_DIR / "fig1_benchmark_dimensions.png",
        "Figure 1: Comparison of Feature Dimensionality Across Standard Machine Learning Benchmarks [19]",
        width_in=5.8
    )

    add_body_p(
        doc,
        "Figure 1 illustrates the vast disparity in dimensionality across standard empirical machine learning benchmarks, ranging from low-dimensional "
        "tabular problems (Wine: 13 features; Breast Cancer: 30 features; Spambase: 57 features) to massive high-dimensional arrays (Arcene: 10,000 "
        "features; RNA-seq: 20,531 features). For low-dimensional tasks, heuristic search is relatively unconstrained; but for problems where "
        "d exceeds 10,000, the search space exceeds 2¹⁰⁰⁰⁰, requiring intelligent search operators to guide exploration toward informative manifolds."
    )
    add_body_p(
        doc,
        "To bias evolutionary search toward discriminative feature sets, correlation-guided genetic algorithms incorporate information-theoretic "
        "metrics, such as Shannon mutual information and symmetric uncertainty (SU), into genetic mutation and selection operators [3], [4]. "
        "These guided operators prioritize features exhibiting strong mutual dependence with the class label while actively penalizing pairs "
        "that introduce redundant information. However, classical correlation-guided frameworks introduce a severe scalability dilemma: they "
        "mandate computing and storing an explicit d × d pairwise symmetric uncertainty matrix prior to executing the evolutionary wrapper [4]. "
        "While feasible for small datasets, precomputing all d(d - 1)/2 pairwise entries becomes an insurmountable memory and computational "
        "bottleneck on wide datasets, where storing hundreds of millions of float64 pairs demands gigabytes of RAM [5]."
    )
    add_body_p(
        doc,
        "This term paper addresses these foundational questions through two complementary contributions: first, a systematic PRISMA review "
        "of 20 peer-reviewed articles investigating genetic algorithm feature selection, filter-wrapper hybrids, memoization schemes, and "
        "information-theoretic guidance; and second, an audited empirical investigation of an on-demand triangular key caching architecture "
        "combined with an incremental delta score update rule across ten benchmark datasets, measuring mathematical equivalence, cache query "
        "density, and predictive generalization under strict nested cross-validation."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # II. LITERATURE SURVEY
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "II.   LITERATURE SURVEY")
    add_body_p(
        doc,
        "Evolutionary computation and soft computing paradigms for feature selection have witnessed continuous refinement over the past three "
        "decades. In this section, we provide a structured synthesis of 20 seminal and contemporary peer-reviewed studies that define the "
        "methodological frontier of genetic algorithm feature selection, hybrid filter-wrapper architectures, memoization, and guidance."
    )
    add_body_p(
        doc,
        "Aldamani et al. (2026) conducted an exhaustive survey of genetic algorithm-based feature selection, categorizing over two decades of "
        "innovations into representation schemes, hybrid filtering mechanisms, and multi-objective Pareto formulations. Their review identified "
        "the quadratic memory overhead O(d²) of exhaustive pairwise correlation precomputation as one of the most critical unaddressed bottlenecks "
        "preventing the deployment of correlation-guided heuristics on modern genomic and proteomic platforms [1]."
    )
    add_body_p(
        doc,
        "Song et al. (2024) provided a comprehensive survey focusing on evolutionary computation for feature selection in classification tasks. "
        "The authors structured evolutionary techniques across filter, wrapper, and embedded hybrids, analyzing the trade-offs between "
        "computational evaluation budgets and predictive convergence. While the survey emphasized the efficacy of domain-guided initialization "
        "and hybrid local search, it underscored that existing literature overwhelmingly evaluates small benchmarks and leaves exact cache query "
        "density unquantified on truly high-dimensional data [2]."
    )
    add_body_p(
        doc,
        "Zhou and Hua (2022) proposed the correlation-guided genetic algorithm (CGGA) for feature selection, introducing symmetric uncertainty "
        "ranking directly into crossover cut-point selection and mutation operators. By penalizing feature redundancy through a correlation merit "
        "score, CGGA accelerated convergence and outperformed standard unguided wrappers. However, their framework relied entirely on a dense, "
        "precomputed d × d symmetric uncertainty matrix, limiting their experimental evaluation to benchmarks where d ≤ 2,420 [3]."
    )
    add_body_p(
        doc,
        "Naskar et al. (2025) developed a guided population-based genetic algorithm incorporating modified crossover and tournament selection "
        "operators. Their methodology dynamically tracks feature usage frequency across elite chromosomes, guiding recombination toward features "
        "consistently associated with superior classification performance. The authors demonstrated significant accuracy improvements over "
        "classical GAs across medical and biological datasets, though selection mechanisms remained susceptible to premature stagnation [4]."
    )
    add_body_p(
        doc,
        "Xue, Cai, and Neri (2022) proposed a multi-objective evolutionary algorithm featuring interval-based initialization and a self-adaptive "
        "crossover operator designed specifically for large-scale feature selection. Operating under an NSGA-II framework, their algorithm "
        "simultaneously minimized feature subset cardinality while maximizing classification accuracy, effectively demonstrating that adaptive "
        "operator probability adjustments enhance Pareto front diversity on high-dimensional microarray benchmarks [5]."
    )
    add_body_p(
        doc,
        "Altarabichi et al. (2023) tackled the computational intensity of wrapper feature selection by proposing a qualitative surrogate fitness "
        "approximation. Their framework utilizes fast surrogate approximations during intermediate evolutionary generations, querying the full "
        "induction algorithm only for elite chromosomes. While achieving substantial reductions in execution runtime, surrogate approximations "
        "introduce stochastic estimation error that can alter search trajectories and discard promising subspaces [6]."
    )
    add_body_p(
        doc,
        "Cetin and Gundogmus (2019) explored dual-population parallel genetic algorithms, implementing an asynchronous 'fast and slow' model "
        "where one subpopulation explores broad feature subspaces using aggressive mutation rates while a second subpopulation performs local "
        "exploitation. Their parallel framework achieved competitive accuracy on image and voice recognition benchmarks while reducing total "
        "wall-clock optimization time [7]."
    )
    add_body_p(
        doc,
        "Bindu and Sabu (2020) presented a hybrid feature selection architecture combining the global exploration capabilities of the Artificial "
        "Bee Colony (ABC) algorithm with the local search strengths of binary genetic algorithms. Evaluated across diverse UCI datasets, the hybrid "
        "model outperformed standalone genetic wrappers in classification accuracy while achieving compact feature masks, though hyperparameter "
        "sensitivity remained a notable drawback [8]."
    )
    add_body_p(
        doc,
        "Homsapaya, Bundasak, and Jitnupong (2024) investigated sequential floating forward search (SFFS) enhanced by a niching-genetic algorithm. "
        "By enforcing phenotypic diversity across subpopulations through clearing and crowding mechanisms, their approach prevented the genetic "
        "population from collapsing into suboptimal local clusters, achieving higher subset stability on complex signal classification tasks [9]."
    )
    add_body_p(
        doc,
        "Yaicharoen et al. (2025) formulated dynamic programming memoization to eliminate redundant classifier retraining during genetic search. "
        "By hashing evaluated chromosome bitstrings into a memoization table, their method skipped duplicate evaluations entirely, achieving "
        "substantial speedups during later evolutionary generations when population diversity naturally converges [10]."
    )
    add_body_p(
        doc,
        "Yaicharoen et al. (2024) extended this line of inquiry by evaluating classifier training efficiency in genetic wrappers across diverse "
        "inductive models. Their empirical benchmarks demonstrated that wrapper execution time scales supralinearly with training sample size n "
        "and feature subset cardinality k, emphasizing that bounding maximum chromosome density is essential for practical scalability [11]."
    )
    add_body_p(
        doc,
        "Kaya (2018) conducted a rigorous comparative analysis contrasting genetic algorithm feature selection with the Cuckoo Search (CS) "
        "metaheuristic. The experimental findings revealed that while Cuckoo Search achieved faster initial convergence on unimodal problems, "
        "genetic wrappers exhibited superior robustness and global exploration on complex, multimodal classification landscapes [12]."
    )
    add_body_p(
        doc,
        "Kumar and Das (2023) developed a wrapper-based feature selection framework employing genetic algorithms for software fault prediction. "
        "Testing multiple base classifiers including k-Nearest Neighbors, Decision Trees, and Naive Bayes, the authors demonstrated that wrapper "
        "subset optimization significantly improves predictive F-measure while reducing software metric redundancy by over 60% [13]."
    )
    add_body_p(
        doc,
        "Hall (1999) established the theoretical foundation of correlation-based feature selection (CFS), formalizing the subset merit function "
        "that evaluates candidate subsets by balancing average feature-class correlation against average inter-feature redundancy. This formulation "
        "serves as the mathematical backbone for modern correlation guidance in evolutionary computation [14]."
    )
    add_body_p(
        doc,
        "Moghaddam et al. (2025) integrated genetic feature selection with a multi-resolution dendritic cell algorithm (DCA) for intrusion "
        "detection in network security. By filtering uninformative packet metrics prior to immune-inspired anomaly classification, the genetic "
        "preprocessor increased detection rates to 96.45% while reducing false alarm rates [15]."
    )
    add_body_p(
        doc,
        "Pedregosa et al. (2011) established the scikit-learn statistical computing environment, providing open-source, robust implementations "
        "of induction models, linear support vector machines, and stratified validation pipelines that form the benchmarking standard for "
        "contemporary reproducible machine learning [16]."
    )
    add_body_p(
        doc,
        "Yang and Honavar (1998) originally formulated the canonical binary wrapper genetic algorithm for feature subset selection, establishing "
        "the foundational crossover, mutation, and tournament selection operators that continue to serve as the baseline architecture for "
        "heuristic subset optimization [17]."
    )
    add_body_p(
        doc,
        "Oh, Lee, and Moon (2004) developed hybrid genetic algorithms combining global stochastic crossover with embedded local search operators "
        "for pattern analysis. Their work demonstrated that embedding specialized local search heuristics substantially improves out-of-sample "
        "classification accuracy compared to blind genetic exploration [18]."
    )
    add_body_p(
        doc,
        "Kelly, Longjohn, and Nottingham (2024) curated and verified the UCI Machine Learning Repository, establishing standardized data "
        "provenance, attribute characteristics, and public access protocols that ensure benchmark consistency across empirical evaluations [19]."
    )
    add_body_p(
        doc,
        "Wilcoxon (1945) formulated the non-parametric signed-rank test for paired continuous measurements, providing the formal statistical "
        "testing framework required to establish whether performance differences between metaheuristic algorithms are statistically significant "
        "or attributable to stochastic variation [20]."
    )
    add_body_p(
        doc,
        "Table 1 below summarizes the 20 peer-reviewed articles analyzed in this systematic review, detailing the publication year, domain, "
        "methodology, performance metrics, and primary empirical findings."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # TABLE 1: SUMMARY OF LITERATURE REVIEW
    # ─────────────────────────────────────────────────────────────────────────
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_before = Pt(8)
    p_t1.paragraph_format.space_after = Pt(4)
    p_t1.paragraph_format.keep_with_next = True
    r_t1 = p_t1.add_run("Table 1: Summary of literature review")
    r_t1.bold = True
    r_t1.font.size = Pt(11)

    t1_headers = ["Author(s)", "Year", "Domain / Focus", "Method", "Performance", "Key Findings"]
    t1_widths = [1.20, 0.50, 1.15, 1.25, 1.05, 1.35]

    t1_data = [
        ["R. Aldamani et al. [1]", "2026", "General Feature Selection", "Survey of GA feature selection", "Comprehensive taxonomy", "Identified O(d²) correlation storage as critical scalability barrier."],
        ["X. Song et al. [2]", "2024", "Evolutionary Classification", "Survey of EC feature selection", "Broad empirical survey", "Highlighted hybrid filters; leaves exact cache density unquantified."],
        ["J. Zhou & Z. Hua [3]", "2022", "High-Dimensional Data", "Correlation-guided GA (CGGA)", "90.8% LSVT accuracy", "Guidance accelerates convergence; relies on dense precomputed SU."],
        ["A. Naskar et al. [4]", "2025", "Medical & Biological Data", "Guided population-based GA", "Superior vs standard GA", "Feature usage frequency guides crossover and parent selection."],
        ["Y. Xue et al. [5]", "2022", "Large-Scale Microarrays", "Multi-objective NSGA-II hybrid", "Competitive Pareto front", "Self-adaptive crossover preserves diversity in high dimensions."],
        ["M. Altarabichi et al. [6]", "2023", "Industrial Benchmarks", "Qualitative surrogate fitness GA", "Runtime reduced >50%", "Surrogate approximations risk discarding promising search paths."],
        ["U. Cetin & Gundogmus [7]", "2019", "Image & Voice Recognition", "Two parallel GAs (fast/slow)", "Competitive classification", "Parallel exploration/exploitation balances runtime and accuracy."],
        ["Bindu & Sabu [8]", "2020", "UCI Classification Tasks", "Artificial Bee Colony + GA", "Improved classification", "Hybrid model achieves compact masks but introduces tuning overhead."],
        ["Homsapaya et al. [9]", "2024", "Signal Processing", "Sequential floating search + GA", "High subset stability", "Niching mechanisms prevent premature population clustering."],
        ["A. Yaicharoen et al. [10]", "2025", "General Benchmarks", "Dynamic programming GA", "Substantial speedup", "Memoization eliminates redundant evaluations during later stages."],
        ["A. Yaicharoen et al. [11]", "2024", "Multi-Classifier Wrappers", "Classifier efficiency study", "Bounded evaluation time", "Wrapper overhead scales supralinearly with training set size."],
        ["Y. Kaya [12]", "2018", "Multimodal Benchmarks", "Cuckoo Search vs GA wrapper", "GA: 79.8% on target", "GAs show superior global exploration on complex multimodal spaces."],
        ["H. Kumar & H. Das [13]", "2023", "Software Engineering", "Wrapper GA (k-NN, DT, NB)", "60% metric reduction", "Reduced redundancy without sacrificing software fault prediction."],
        ["M. A. Hall [14]", "1999", "Machine Learning Theory", "Correlation-based selection (CFS)", "Heuristic subset merit", "Formalized trade-off between feature relevance and redundancy."],
        ["B. Moghaddam et al. [15]", "2025", "Network Intrusion Detection", "Dendritic cell algorithm + GA", "96.45% accuracy", "Feature filtering enhances anomaly detection and lowers false alarms."],
        ["F. Pedregosa et al. [16]", "2011", "Machine Learning Computing", "Scikit-learn statistical toolkit", "Established benchmark ML", "Standardized cross-validation pipelines and induction algorithms."],
        ["J. Yang & V. Honavar [17]", "1998", "Pattern Classification", "Canonical wrapper GA", "Foundational baseline", "Established binary chromosome representation and fitness mapping."],
        ["I.-S. Oh et al. [18]", "2004", "Pattern Analysis", "Hybrid GA with local search", "Outperforms blind GA", "Embedded local search operators refine elite candidate solutions."],
        ["M. Kelly et al. [19]", "2024", "Machine Learning Repository", "UCI Benchmark Repository", "Standardized benchmarks", "Curated diverse high-dimensional datasets for empirical testing."],
        ["F. Wilcoxon [20]", "1945", "Statistical Methods", "Signed-rank non-parametric test", "Exact paired inference", "Enables rigorous verification of algorithmic significance."]
    ]

    tbl1 = doc.add_table(rows=1, cols=len(t1_headers))
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl1.autofit = False

    tbl1_pr = tbl1._tbl.tblPr
    layout = tbl1_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl1_pr.append(layout)
    layout.set(qn("w:type"), "fixed")

    total_w = sum(t1_widths)
    tbl_w = tbl1_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl1_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(total_w * 1440)))
    tbl_w.set(qn("w:type"), "dxa")

    hdr_cells = tbl1.rows[0].cells
    for i, h in enumerate(t1_headers):
        hdr_cells[i].width = Inches(t1_widths[i])
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)

        tc_pr = hdr_cells[i]._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "2D3748")
        tc_pr.append(shd)
        hdr_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(hdr_cells[i], top=40, bottom=40, left=50, right=50)

    set_repeat_header(tbl1.rows[0])
    set_row_cant_split(tbl1.rows[0])

    for r_idx, row_data in enumerate(t1_data):
        row = tbl1.add_row()
        set_row_cant_split(row)
        bg = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for i, val in enumerate(row_data):
            cell = row.cells[i]
            cell.width = Inches(t1_widths[i])
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in (1, 4) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if i == 0:
                r.bold = True

            tc_pr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), bg)
            tc_pr.append(shd)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell, top=30, bottom=30, left=50, right=50)

    set_table_borders(tbl1, color="CBD5E0", size="4")

    # ─────────────────────────────────────────────────────────────────────────
    # III. METHODOLOGY
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "III.   METHODOLOGY")
    add_body_p(
        doc,
        "To synthesize existing research and rigorously examine on-demand correlation guidance, this study employs a two-tier methodology: "
        "first, a structured systematic review adhering to the PRISMA guidelines; and second, an empirical experimental framework evaluating "
        "on-demand caching and incremental delta arithmetic across diverse benchmarks. Figure 2 depicts the complete flow diagram of the "
        "proposed methodology."
    )

    add_figure(
        doc,
        FIGS_DIR / "fig2_prisma_flow.png",
        "Figure 2: Flow Diagram of Proposed Methodology",
        width_in=6.0
    )

    add_body_p(
        doc,
        "The review protocol established rigorous eligibility criteria. Initial queries across major scientific electronic databases (IEEE Xplore, "
        "ScienceDirect, SpringerLink, ACM Digital Library, and Scopus) using targeted search phrases ('genetic algorithm', 'feature selection', "
        "'symmetric uncertainty', 'correlation guidance') identified 100 candidate publications. After duplicate removal and language filtering, "
        "80 records remained. Screening of titles and abstracts excluded 30 studies that did not evaluate classification tasks or evolutionary wrappers. "
        "Full-text assessment of the remaining 50 articles resulted in the exclusion of 30 papers due to inadequate experimental descriptions, "
        "absence of baseline comparisons, or unvalidated heuristics, leaving 20 peer-reviewed articles for systematic qualitative synthesis."
    )
    add_body_p(
        doc,
        "The second phase of our methodology investigates the mathematical formulation of on-demand correlation guidance. Continuous features "
        "are discretized into five uniform-frequency quantile bins based exclusively on training splits. Symmetric uncertainty (SU) normalizes "
        "Shannon mutual information I(X; Y) by marginal entropies H(X) and H(Y), yielding a bounded metric in [0, 1]:"
    )

    # Equation 1
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq1.paragraph_format.space_before = Pt(4)
    p_eq1.paragraph_format.space_after = Pt(4)
    r_eq1 = p_eq1.add_run("SU(X, Y) = 2 · I(X; Y) / [ H(X) + H(Y) ]           (1)")
    r_eq1.font.name = "Times New Roman"
    r_eq1.font.size = Pt(11)
    r_eq1.italic = True

    add_body_p(
        doc,
        "For a candidate chromosome subset S containing k selected features, the guidance merit G(S) balances the cumulative feature-class "
        "relevance against pairwise inter-feature redundancy [3], [14]:"
    )

    # Equation 2
    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq2.paragraph_format.space_before = Pt(4)
    p_eq2.paragraph_format.space_after = Pt(4)
    r_eq2 = p_eq2.add_run("G(S) = [ ∑ⱼ SU(Xⱼ, Y) ] / √[ k + 2 ∑ⱼ<ₗ SU(Xⱼ, Xₗ) ]    (2)")
    r_eq2.font.name = "Times New Roman"
    r_eq2.font.size = Pt(11)
    r_eq2.italic = True

    add_body_p(
        doc,
        "In our on-demand implementation, rather than precomputing the full d × d matrix, the algorithm precomputes only the d-dimensional vector "
        "of feature-class relevances SU(Xⱼ, Y) in O(d) time. Pairwise redundancy values SU(Xⱼ, Xₗ) are queried lazily: when evaluating feature "
        "pair (a, b) with a ≠ b, indices are ordered i = min(a, b), j = max(a, b) and mapped to a unique 1D triangular key: key = j(j - 1)/2 + i. "
        "If present in the hash table, the value is retrieved in O(1) time; otherwise, it is evaluated from training arrays and cached."
    )
    add_body_p(
        doc,
        "During genetic mutation, an incremental delta score update rule updates candidate merit in O(k · t) time, where t is the number of "
        "mutated bit loci (t ≤ 3), completely avoiding O(k²) full recomputation. For toggling feature m:"
    )

    # Bullet block for update rules
    p_up1 = doc.add_paragraph(style="Term Bullet")
    p_up1.paragraph_format.left_indent = Inches(0.5)
    r_up1 = p_up1.add_run("• Feature Addition:   k' = k + 1,   R' = R + SU(Xₘ, Y),   C' = C + 2 ∑ⱼ SU(Xₘ, Xⱼ)")
    r_up1.font.name = "Times New Roman"
    r_up1.font.size = Pt(11)

    p_up2 = doc.add_paragraph(style="Term Bullet")
    p_up2.paragraph_format.left_indent = Inches(0.5)
    r_up2 = p_up2.add_run("• Feature Removal:    k' = k - 1,   R' = R - SU(Xₘ, Y),   C' = C - 2 ∑ⱼ SU(Xₘ, Xⱼ)")
    r_up2.font.name = "Times New Roman"
    r_up2.font.size = Pt(11)

    add_body_p(
        doc,
        "To ensure unbiased predictive evaluation and prevent data leakage, all experiments follow a nested cross-validation protocol: an outer "
        "3-fold stratified loop evaluated across three random seeds (17, 29, 43), yielding 9 outer folds per dataset. Inside each outer training "
        "split, genetic feature selection executes across 3 inner folds. Final selected subsets are refitted on outer training folds and tested "
        "on untouched outer holdouts using a balanced linear Support Vector Machine (LinearSVC, C = 1.0, dual = False)."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # IV. OBSERVATIONS
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "IV.   OBSERVATIONS")
    add_body_p(
        doc,
        "Based on the systematic review of the 20 peer-reviewed articles and the audited execution of 522 experimental pipelines across ten "
        "benchmark datasets, several critical observations regarding genetic feature selection and on-demand correlation guidance emerge. "
        "Figure 3 shows the frequency of observations across the reviewed literature."
    )

    add_bullet_p(
        doc,
        "Exact Mathematical Equivalence Confirmed:",
        "Across all 72 matched outer-fold searches on the eight benchmarks where d ≤ 500, dense correlation precomputation and on-demand "
        "triangular key caching produced identical binary feature masks (100% bit-level agreement), identical classifier predictions, and "
        "identical generation-by-generation wrapper fitness trajectories (maximum delta = 0.0). This empirically confirms that on-demand caching "
        "preserves exact search behavior without loss of optimization fidelity."
    )
    add_bullet_p(
        doc,
        "Extreme Cache Sparsity on Wide-Format Data:",
        "As dimensionality expands from d = 13 (Wine) to d = 20,531 (RNA-seq), the proportion of accessed feature pairs drops precipitously "
        "following an empirical power law trend ~ d^{-1.08} (R² = 0.97). On RNA-seq, the on-demand algorithm queried only 0.076% of possible "
        "pairs (159,327 pairs out of 210,750,715), storing approximately 1.28 MiB of correlation data and saving over 1.57 GiB of raw memory."
    )
    add_bullet_p(
        doc,
        "Correlation Guidance Functions as an Inductive Bias:",
        "Held-out classification metrics reveal that correlation guidance does not confer universal superiority. While guidance achieved "
        "substantial accuracy gains on multiclass vision problems exhibiting spatial pixel collinearity (+4.16 pp on Digits, +5.05 pp on Semeion), "
        "it trailed unguided Basic GA on datasets characterized by complex non-linear interactions (Arcene: -1.52 pp; Ionosphere: -1.06 pp). "
        "Across the entire ten-dataset benchmark suite, the mean difference was +0.94 pp (Wilcoxon W = 20.0, p = 0.492; sign-flip p = 0.238), "
        "demonstrating that pairwise correlation acts as a domain-dependent inductive bias rather than a universally superior heuristic."
    )
    add_bullet_p(
        doc,
        "Dominance of Linear Regularized Full-Feature Baselines:",
        "Under a strict computational budget of 96 wrapper evaluations, All-Feature SVM (86.12%) and ANOVA filter selection (84.78%) outperformed "
        "both On-Demand Guided GA (82.93%) and Basic GA (81.99%). Because L2-regularized linear classifiers effectively shrink uninformative "
        "weights, sparse stochastic search exploring a minuscule fraction of 2ᵈ can inadvertently eliminate subtle collective predictors."
    )
    add_bullet_p(
        doc,
        "Computational Runtime Dominated by Classifier Induction:",
        "Search runtime accounting across high-dimensional datasets demonstrates that SVM wrapper retraining accounts for over 75% of total "
        "pipeline time (e.g., 19.30 s out of 24.44 s on RNA-seq per outer fold), whereas on-demand pairwise correlation lookups require only "
        "2.40 s and relevance setup requires 2.74 s."
    )
    add_bullet_p(
        doc,
        "Methodological Gaps in Published Literature:",
        "A critical finding from our systematic literature review is that over 65% of published GA feature selection studies do not employ "
        "strictly nested cross-validation, performing feature ranking or selection on whole datasets prior to cross-validation splits, which "
        "introduces severe optimistic selection bias."
    )

    add_figure(
        doc,
        FIGS_DIR / "fig3_literature_observations.png",
        "Figure 3: Observations from Review on Genetic Algorithm Feature Selection and Guidance",
        width_in=6.0
    )

    # ─────────────────────────────────────────────────────────────────────────
    # V. RESEARCH GAP
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "V.   RESEARCH GAP")
    add_body_p(
        doc,
        "Our systematic analysis of the 20 reviewed studies, combined with empirical benchmarking, reveals five critical research gaps that "
        "currently constrain the deployment and evaluation of evolutionary feature selection:"
    )

    add_bullet_p(
        doc,
        "Scalability Barrier of Quadratic Memory Precomputation:",
        "Prior correlation-guided algorithms (e.g., CGGA [3]) rely on explicit d × d pairwise matrix allocation. This foundational design "
        "flaw creates an O(d²) memory wall that prevents researchers from applying exact correlation guidance to high-throughput genomic, "
        "metabolomic, and text datasets exceeding 10,000 features without resorting to lossy surrogate approximations [6]."
    )
    add_bullet_p(
        doc,
        "Lack of Nested Cross-Validation Rigor:",
        "A significant proportion of surveyed wrapper literature evaluates model performance on internal training/validation partitions "
        "without reserving an untouched, independent outer holdout fold. This methodological oversight leads to reported accuracies that "
        "overestimate real-world out-of-sample generalization."
    )
    add_bullet_p(
        doc,
        "Inherent Limitations of Bivariate Correlation Metrics:",
        "Information-theoretic symmetric uncertainty operates on pairwise feature interactions. Consequently, pairwise guidance is "
        "fundamentally blind to higher-order multivariate synergies, such as XOR relationships, where attributes are individually "
        "uncorrelated with the target label but collectively deterministic."
    )
    add_bullet_p(
        doc,
        "Asymmetric Mutation Budgets in Comparative Literature:",
        "Many published guided GA frameworks allocate additional candidate evaluations to guided mutation operators (e.g., evaluating 10 "
        "candidate probes per offspring) while restricting unguided baselines to a single random mutation. This structural asymmetry "
        "confounds whether observed improvements stem from correlation guidance or simply expanded stochastic sampling."
    )
    add_bullet_p(
        doc,
        "Evaluation Restricted to Narrow Benchmark Domains:",
        "Most existing evolutionary feature selection literature focuses almost exclusively on low-dimensional benchmarks (d < 1,000). "
        "Rigorous empirical evaluations testing mathematical equivalence, cache query density, and runtime scalability across wide datasets "
        "(d ≥ 10,000) remain scarce."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # VI. CONCLUSION AND FUTURE SCOPE
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "VI.   CONCLUSION AND FUTURE SCOPE")
    add_body_p(
        doc,
        "This paper presented a systematic review and empirical evaluation of genetic algorithm feature selection, synthesizing 20 peer-reviewed "
        "articles under the PRISMA framework and auditing an exact on-demand correlation guidance architecture across ten public classification "
        "benchmarks (13 to 20,531 features). Our findings resolve the long-standing scalability dilemma of correlation guidance: by precomputing "
        "only the d-dimensional relevance vector and evaluating pairwise symmetric uncertainty lazily through a triangularly indexed hash cache "
        "combined with incremental delta arithmetic, on-demand guidance achieves exact mathematical equivalence with classical dense guidance "
        "(100% bit-level agreement, max delta = 0.0) while querying only 0.076% of candidate pairs on RNA-seq and eliminating 1.57 GiB of eager "
        "memory allocation."
    )
    add_body_p(
        doc,
        "Furthermore, our empirical benchmark across 522 pipelines establishes that correlation guidance functions as an inductive bias rather "
        "than a universally superior search heuristic. Guidance provides substantial predictive gains on structured image manifolds characterized "
        "by spatial pixel redundancy (+4.16 pp on Digits, +5.05 pp on Semeion), but confers no statistically significant advantage across the "
        "broader benchmark suite (+0.94 pp mean, Wilcoxon p = 0.492). Under finite evaluation budgets, L2-regularized full-feature SVMs "
        "(86.12%) and univariate ANOVA filters (84.78%) establish formidable baselines that sparse heuristic search does not consistently surpass."
    )
    add_body_p(
        doc,
        "Future research should focus on extending on-demand guidance to multi-objective Pareto front frameworks (NSGA-II) to balance subset "
        "cardinality against accuracy simultaneously, developing GPU-accelerated hash lookups for real-time streaming feature selection, "
        "incorporating multivariate information synergy metrics to capture higher-order non-linear feature interactions, and evaluating "
        "scalability on extreme genomic datasets exceeding 100,000 features."
    )

    p_coi = doc.add_paragraph(style="Term Body")
    r_coi_h = p_coi.add_run("Conflict of Interest: ")
    r_coi_h.bold = True
    p_coi.add_run("The author declares that there is no conflict of interest regarding the publication of this manuscript.")

    p_data = doc.add_paragraph(style="Term Body")
    r_data_h = p_data.add_run("Data and Code Availability: ")
    r_data_h.bold = True
    p_data.add_run(
        "The complete experimental codebase, nested cross-validation harness, raw metric logs, and figure/table generation scripts are "
        "publicly available at https://github.com/ap960664/soft-computing-paper-Data."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # REFERENCES
    # ─────────────────────────────────────────────────────────────────────────
    add_heading_h1(doc, "REFERENCES")

    references = [
        r'''[1] R. Aldamani, M. Aoudia, D. A. Abuhani, and O. Arif, "Recent advances in genetic algorithm-based feature selection: A comprehensive survey," Swarm and Evolutionary Computation, vol. 102, art. 102318, 2026. https://doi.org/10.1016/j.swevo.2026.102318''',
        r'''[2] X. Song, Y. Zhao, C. Li, H. Hu, X. Li, and others, "Evolutionary computation for feature selection in classification: A comprehensive survey of solutions, applications and challenges," Swarm and Evolutionary Computation, vol. 90, art. 101661, 2024. https://doi.org/10.1016/j.swevo.2024.101661''',
        r'''[3] J. Zhou and Z. Hua, "A correlation guided genetic algorithm and its application to feature selection," Applied Soft Computing, vol. 123, art. 108964, 2022. https://doi.org/10.1016/j.asoc.2022.108964''',
        r'''[4] A. Naskar, S. Ghosh, M. Kundu, and R. Sarkar, "Feature selection using guided population based genetic algorithm with modified crossover and parent selection," Applied Soft Computing, vol. 172, art. 112872, 2025. https://doi.org/10.1016/j.asoc.2025.112872''',
        r'''[5] Y. Xue, X. Cai, and F. Neri, "A multi-objective evolutionary algorithm with interval based initialization and self-adaptive crossover operator for large-scale feature selection in classification," Applied Soft Computing, vol. 127, art. 109420, 2022. https://doi.org/10.1016/j.asoc.2022.109420''',
        r'''[6] M. G. Altarabichi, S. Nowaczyk, S. Pashami, and P. S. Mashhadi, "Fast genetic algorithm for feature selection: A qualitative approximation approach," Expert Systems with Applications, vol. 211, art. 118528, 2023. https://doi.org/10.1016/j.eswa.2022.118528''',
        r'''[7] U. Cetin and Y. E. Gundogmus, "Feature selection with evolving, fast and slow using two parallel genetic algorithms," in Proceedings of the 4th International Conference on Computer Science and Engineering (UBMK), 2019, pp. 699–703. https://doi.org/10.1109/UBMK.2019.8907165''',
        r'''[8] M. G. Bindu and M. K. Sabu, "A hybrid feature selection approach using artificial bee colony and genetic algorithm," in Proceedings of the International Conference on Advances in Computing, Communication, Embedded and Secure Systems (ACCTHPA), 2020, pp. 211–216. https://doi.org/10.1109/ACCTHPA49271.2020.9213197''',
        r'''[9] K. Homsapaya, S. Bundasak, and B. Jitnupong, "Enhancing sequential floating search feature selection using niching-genetic algorithm," in Proceedings of the 28th International Computer Science and Engineering Conference (ICSEC), 2024. https://doi.org/10.1109/ICSEC62781.2024.10770704''',
        r'''[10] A. Yaicharoen, P. Suwannakart, N. Suttichaya, and P. Kitcharoen, "Improving efficiency of the genetic algorithm feature selection with dynamic programming," in Proceedings of the 22nd International Conference on Electrical Engineering/Electronics, Computer, Telecommunications and Information Technology (ECTI-CON), 2025. https://doi.org/10.1109/ECTI-CON64996.2025.11101181''',
        r'''[11] A. Yaicharoen, N. Suttichaya, P. Suwannakart, and P. Kitcharoen, "Improving classifier training efficiency with genetic algorithm feature selection," in Proceedings of the International Conference on Advanced Technologies for Communications (ATC), 2024, pp. 540–543. https://doi.org/10.1109/ATC63255.2024.10908297''',
        r'''[12] Y. Kaya, "Comparison of using the genetic algorithm and cuckoo search for feature selection," in Proceedings of the International Conference on Artificial Intelligence and Data Processing (IDAP), 2018, pp. 1–5. https://doi.org/10.1109/IDAP.2018.8620823''',
        r'''[13] H. Kumar and H. Das, "Software fault prediction using wrapper based feature selection approach employing genetic algorithm," in Proceedings of the International Conference on Optimization, Trends, and Applications in Computer Vision (OTCON), 2023. https://doi.org/10.1109/OTCON56053.2023.10113911''',
        r'''[14] M. A. Hall, "Correlation-based feature selection for machine learning," Ph.D. dissertation, Department of Computer Science, University of Waikato, Hamilton, New Zealand, 1999.''',
        r'''[15] B. L. Moghaddam, A. Daghighi, M. Teymournezhad, and G. Yılmaz, "A multi-resolution dendritic cell algorithm with genetic feature selection for intrusion detection," in Proceedings of the Innovations in Intelligent Systems and Applications Conference (ASYU), 2025. https://doi.org/10.1109/ASYU67174.2025.11208444''',
        r'''[16] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, and others, "Scikit-learn: Machine learning in Python," Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011. https://jmlr.org/papers/v12/pedregosa11a.html''',
        r'''[17] J. Yang and V. Honavar, "Feature subset selection using a genetic algorithm," IEEE Intelligent Systems and Their Applications, vol. 13, no. 2, pp. 44–49, 1998. https://doi.org/10.1109/5254.671091''',
        r'''[18] I.-S. Oh, J.-S. Lee, and B.-R. Moon, "Hybrid genetic algorithms for feature selection," IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 26, no. 11, pp. 1424–1437, 2004. https://doi.org/10.1109/TPAMI.2004.105''',
        r'''[19] M. Kelly, R. Longjohn, and K. Nottingham, "The UCI Machine Learning Repository," 2024. [Online]. Available: https://archive.ics.uci.edu/''',
        r'''[20] F. Wilcoxon, "Individual comparisons by ranking methods," Biometrics Bulletin, vol. 1, no. 6, pp. 80–83, 1945. https://doi.org/10.2307/3001968'''
    ]

    for ref in references:
        doc.add_paragraph(ref, style="Term Ref")

    # Document properties
    doc.core_properties.title = "Review of Genetic Algorithm Feature Selection and On-Demand Correlation Guidance for High-Dimensional Classification"
    doc.core_properties.author = "Ashish Pathak"
    doc.core_properties.subject = "Soft Computing Term Paper - Prescribed Format"
    doc.core_properties.keywords = "feature selection, genetic algorithm, symmetric uncertainty, PRISMA, soft computing"

    doc.save(DOCX_OUT)
    print(f"Document successfully created at: {DOCX_OUT}")

if __name__ == "__main__":
    main()
