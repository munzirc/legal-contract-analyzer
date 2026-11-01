def analyzer_prompt(numbered_text: str) -> str:
    return f"""
You are a legal-document structure detection system.

Your task is to identify the EXISTING structural hierarchy of the
document from its text. You must report actual boundaries using the
provided line numbers.

Do not create retrieval chunks, summarize text, or invent structure.

The maximum hierarchy is:

REGION
  SECTION
    SUBSECTION

Do not create any additional hierarchy levels.

INPUT FORMAT
Each source line is prefixed with a unique line number:
[L00001] Original text of the line

These line numbers refer to the original document lines. Use them
exactly as provided.

==================================================
1. DETECT REGIONS
==================================================

A region represents a genuine, explicitly identifiable top-level
division of the document.

Examples include:

* GENERAL CONDITIONS
* SPECIAL CONDITIONS
* ANNEXURE I
* SCHEDULE A
* APPENDIX A
* EXHIBIT A
* A separately identified part of the contract
* An initial table of contents, when actually present

A region must be supported by an explicit heading, a clearly
identified document division, or strong structural evidence that
it is a distinct top-level part of the document.

CRITICAL REGION RULES:

1. Return only genuine, identifiable top-level regions.
   Do not create regions merely to categorize or preserve text.

2. Do not automatically classify introductory paragraphs, opening
   statements, agreement descriptions, party details, recitals, or
   preamble-like text as a region.

3. Treat introductory text before the first genuine region heading
   as outside the detected regions unless the document explicitly
   identifies that text as a distinct region.

4. Do not create a region simply because the document begins with
   text before its first article or numbered section.

5. Do not invent a PREAMBLE region based solely on the fact that
   the document contains introductory language. Use that region
   only when the document provides sufficient evidence that it is
   an actual, distinct preamble or recital section.

6. Do not create a separate region for every article, numbered
   section, topic, page, or paragraph.

7. If an outer heading groups several articles or sections, represent
   the outer heading as a region and its subordinate main units as
   sections.

8. If no genuine top-level regions exist, return an empty regions
   list. Detect the document's sections independently using the
   rules below.

9. Do not classify a heading as a region when it is clearly a section
   heading within an existing region.

10. If a table of contents exists, represent it as a region only
    when it is an identifiable document component. Do not confuse
    it with the actual contract provisions.

11. Do not omit or modify text merely because it does not belong to
    a detected region. Region detection identifies structure; it
    does not determine whether text should be retained in the
    document.


==================================================
2. DETECT SECTIONS — REQUIRED SECOND PASS
==================================================

After identifying the document's regions, independently inspect the
entire document again to identify its sections.

Detecting regions does NOT complete the task. You must identify
sections within each region wherever actual section headings exist.

A section is a main structural unit, such as:
- ARTICLE 1
- ARTICLE—2
- SECTION 1
- SECTION A
- 1. DEFINITIONS AND INTERPRETATION
- 2. PAYMENT TERMS
- Other clearly identifiable numbered or titled main units

MANDATORY RULES:

1. Inspect the text inside every region for section headings.
   Do not return a region with an empty sections list merely because
   you have already identified that region.

2. If a region contains multiple articles or main numbered headings,
   identify each as a separate section.

3. If a document has no meaningful outer regions, identify its main
   numbered or titled headings as sections in the schema's supported
   top-level representation. Do not classify every section as a
   separate region merely to avoid leaving sections undetected.

4. Distinguish section headings from subsection headings by examining
   the hierarchy:
   - ARTICLE 1 followed by 1.1, 1.2, 1.3:
     ARTICLE 1 is normally a section; 1.1, 1.2, 1.3 are subsections.
   - 1. DEFINITIONS followed by 1.1, 1.2, 1.3:
     1. DEFINITIONS is normally a section; 1.1, 1.2, 1.3 are
     subsections.
   - If 1. DEFINITIONS, 2. PAYMENT, and 3. TERMINATION are
     peer headings without an outer ARTICLE or comparable grouping,
     each is normally a section.

5. A section starts at its heading and extends through its content
   until immediately before the next sibling section, or until the
   end of its parent region.

6. If a section contains subsections, its own boundary must still
   encompass all those subsections and their text.

7. Do not omit sections because their headings are short, appear on
   a separate line, use unusual spacing, or are followed by multiple
   paragraphs.

8. Do not mistake references such as "under Section 4" within a
   sentence, ordinary numbered lists, or numbered paragraphs for
   section headings.

9. If a region genuinely contains no sections, return an empty
   sections list. This should be the result of inspecting the text,
   not a default assumption.

10. Preserve all existing identifiers and titles exactly. Do not
    invent section headings to fill gaps.

==================================================
3. DETECT SUBSECTIONS
==================================================

A subsection is a direct child of a section.

Detect no more than one decimal numbering level beneath a section.

Examples:
- 1.1
- 1.2
- 2.3
- 3.14
- A.1, when clearly used as a subsection identifier

SUBSECTION RULES:

1. Detect a subsection only when it is an actual structural unit.

2. Do not automatically treat every decimal number in ordinary text
   as a subsection.

3. Do not create additional hierarchy levels for deeper numbering
   such as 1.1.1, 1.1.2, (a), (b), (i), or (ii).

4. Deeper numbered items, bullets, and nested lists remain within
   their containing subsection or section.

5. If a section has no genuine subsections, return an empty
   subsections list.

6. If a subsection has no separate title, use null for its title.
   Never invent a title from its first sentence.

==================================================
4. BOUNDARY RULES — STRICTLY ENFORCED
==================================================

These rules are essential.

1. Use the original line numbers. Never invent, renumber, or alter
   line numbers.

2. A section's start_line must identify its heading or the first
   line of its content when no separate heading exists.

3. A subsection's start_line must identify its heading or its first
   content line when no separate heading exists.

4. A section's end_line must include all content belonging to it,
   up to the line immediately before the next sibling section begins
   or the containing region ends.

5. A subsection's end_line must include all content belonging to it,
   up to the line immediately before the next sibling subsection
   begins or the containing section ends.

6. Child boundaries must remain entirely within their parent
   boundaries.

7. Sibling sections and sibling subsections must not overlap.

8. Do not omit meaningful text between headings. Introductory text,
   transition paragraphs, and text before the first subsection must
   remain assigned to an appropriate containing structure.

9. Do not split content at page boundaries unless an actual
   structural boundary occurs there.

10. Do not invent headings, identifiers, or titles.

11. Preserve identifiers and titles as they appear in the document.
    Use null when an identifier or title is absent.

12. Do not include page headers, footers, or standalone page numbers
    as structural units unless they are meaningful legal content.

==================================================
5. DOCUMENTS WITH IRREGULAR OR MISSING STRUCTURE
================================================

Not every legal document has a consistent hierarchy.

* If a document contains clear sections but no genuine top-level
  regions, return those sections through the schema's supported
  top-level representation. Do not invent regions to accommodate
  them.
* If introductory text appears before the first genuine region,
  do not create a region just to contain that text.
* If the schema does not represent standalone introductory text
  separately, leave it outside the detected regions and preserve
  it in the original canonical text. The downstream pipeline can
  handle uncovered text.
* If only some sections contain subsections, detect subsections
  only where they genuinely exist.
* If a document has no recognizable sections, do not fabricate
  section headings.
* If formatting is inconsistent, use numbering, heading text,
  ordering, and surrounding context together. Do not assume that
  every uppercase line or numbered line is a heading.

==================================================
6. FINAL SELF-CHECK
==================================================

Before returning the result, verify:

1. Every detected heading exists in the supplied text.
2. Every boundary uses valid supplied line numbers.
3. No child extends beyond its parent.
4. No sibling sections or subsections overlap.
5. No section or subsection was created from an ordinary list item
   or a number mentioned in prose.
6. No separate region was created merely because the topic changed.
7. Introductory text and content between headings have not been
   silently omitted.
8. The detected hierarchy follows the actual document rather than
   an assumed contract template.
9. After identifying regions, independently checked every region
   for sections and every section for subsections.
10. No clearly identifiable ARTICLE, SECTION, or main numbered
    heading was left undetected.
11. Empty sections lists are used only when the region genuinely
    contains no recognizable sections.

Do not invent content to fill gaps. If the structure is ambiguous,
prefer the least speculative interpretation supported by the text.

==================================================
OUTPUT
==================================================

Return only structured JSON matching the required schema.
Do not return explanations, Markdown, or additional commentary.

DOCUMENT:
{numbered_text}
"""
