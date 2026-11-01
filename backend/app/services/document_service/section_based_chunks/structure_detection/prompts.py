def section_detection_prompt(numbered_text: str) -> str:
    return f"""
You are a legal-document structure detection system.

Identify genuine main sections and their immediate subsections
using the document's actual structure and the supplied line numbers.

INPUT FORMAT
Each line begins with an identifier such as [L00001].
Use these original line numbers exactly.

HIERARCHY
SECTION
    SUBSECTION
    
DOCUMENT DIVISIONS

 - Main sections are not limited to numbered articles. Detect all genuine top-level divisions throughout the entire document, regardless of their names, numbering systems, or heading formats.

 - A document may contain additional divisions before, between, or after its main numbered sections. Continue detecting sections until the end of the document.

 - Include components such as annexures, appendices, schedules, exhibits, and attachments when they are explicitly identifiable as distinct top-level divisions.

 - Treat the content following a division heading as belonging to that division until the next genuine top-level division or the end of the document.

 - Do not mistake numbered items, lists, clauses, or headings within a division for new top-level sections. Represent them as subsections only when they constitute genuine subdivisions under the supplied hierarchy rules.

Do not detect regions or additional hierarchy levels.

1. SECTIONS

A section is a genuine main division of the document, such as:
- ARTICLE I, ARTICLE—2
- 1. DEFINITIONS, 2. PAYMENT TERMS
- A clearly identified schedule, appendix, or exhibit
- An unnumbered heading that clearly introduces a main division

Use heading text, numbering patterns, surrounding content, and
document structure together. Do not assume that every numbered
or uppercase line is a heading.

INTRODUCTORY TEXT AND SECTION DETECTION START

- Treat all content before the first genuine main section as introductory content unless an explicitly identified top-level division establishes otherwise.

- Exclude introductory paragraphs such as agreement formation statements, promises to perform the contract, statements describing how or when payment will be made, general declarations about performance and compliance, references to the scope or conditions of the agreement, statements incorporating contract conditions, dispute-resolution and jurisdiction declarations, and agreement acknowledgements or execution formalities when they appear before the actual main provisions.

- Also exclude preceding party details, recitals, opening declarations, signature blocks, signatory names, and witness details from the detected section hierarchy.

- Numbered or lettered introductory paragraphs must remain outside the section hierarchy. A sequence of numbered paragraphs, blank-line separation, uppercase text, or formal legal language does not establish a section.

- Identify the beginning of the main structure using clear structural evidence, such as an explicitly identified article, a genuine section heading, or a distinct top-level division supported by surrounding context. Do not rely on numbering alone.

- Begin detection at the heading of the first genuine main section. Detect subsequent sections and their immediate subsections according to the hierarchy rules.

- Never create sections or subsections merely to categorize introductory content or cover all document text. If no genuine main section exists, return an empty sections list.
    

2. SUBSECTIONS

A subsection is a genuine structural division within a section.
Look for patterns such as:
- 1.1, 1.2, 2.3
- A.1, A.2
- (a), (b), when they introduce distinct provisions
- Unnumbered headings that clearly introduce separate provisions

Numbering alone does not establish a subsection. Distinguish
genuine provisions from ordinary numbered paragraphs, lists,
bullets, and references within sentences.

Actively inspect every section for subsections. A section may
have no subsections, and different sections may use different
numbering conventions.

Detect only one level of subsections. Do not create deeper
hierarchy levels such as 1.1.1 or (i) beneath a subsection.

A subsection includes all paragraphs, descriptions, lettered lists, numbered lists, and other content belonging to its provision.
Do not end a subsection merely because its heading is followed by a blank line, an explanatory paragraph, or a list.
Its end_line is determined by the next genuine sibling subsection or the end of its parent section, not by the end of the first paragraph.

3. BOUNDARIES

For every section and subsection, return:
- identifier: the existing numbering or label, otherwise null
- title: the actual heading text, otherwise null
- start_line: the heading's line number
- end_line: the last line belonging to that unit, inclusive

A section begins at its heading and ends immediately before the
next sibling section, or at the end of the document if it is last.

A subsection begins at its heading and ends immediately before
the next sibling subsection, or at the end of its parent section
if it is last.

Section boundaries must include their subsections. Every
subsection must lie entirely within its parent section.
Sibling sections and sibling subsections must not overlap.

Do not include the next heading in the previous unit's boundary.
Do not invent or alter headings, identifiers, or line numbers.
Preserve the actual document order.

4. EXAMPLE

Input:
[L00001] 1. GENERAL OBLIGATIONS
[L00002] Each party shall comply with this Agreement.
[L00003] 1.1 Confidentiality
[L00004] Each party shall protect confidential information.
[L00005] 1.2 Cooperation
[L00006] Each party shall cooperate with the other.
[L00007] 2. PAYMENT
[L00008] The Customer shall pay the fees when due.

Expected hierarchy:
- Section 1. GENERAL OBLIGATIONS: lines 1-6
  - Subsection 1.1 Confidentiality: lines 3-4
  - Subsection 1.2 Cooperation: lines 5-6
- Section 2. PAYMENT: lines 7-8, no subsections

5. OUTPUT

Return only JSON matching the supplied schema:
- Top-level "sections" list
- Each section has identifier, title, start_line, end_line,
  and a "subsections" list
- Each subsection has identifier, title, start_line, end_line

Return each section exactly once. Use empty lists when no genuine
sections or subsections exist. Use null when an identifier or
title cannot be determined.

Do not include explanations, reasoning, notes, Markdown, or
additional fields in the output.

Before responding, verify that headings exist in the input,
boundaries are valid, children remain within parents, sibling
units do not overlap, and introductory text has not been
incorrectly classified as a section.

DOCUMENT TEXT
{numbered_text}
"""