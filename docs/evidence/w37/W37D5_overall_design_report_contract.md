# W37-D5 Overall Design Summary and Report Contract

## 1. Purpose

W37-D5 provides a readable summary/report layer for OverallSupportDesign v1.

The report layer consumes an already-built OverallSupportDesign object.

It does not perform engineering calculations and does not modify the design.

## 2. Three-level parameter distinction

The report shall preserve three different engineering meanings:

- reference value
- requirement value
- design value

Example for working resistance:

reference_support.working_resistance_kn
= historical/reference support value

support_requirement.required_working_resistance_kn
= deterministic requirement calculation result

overall_parameters.design_working_resistance_kn
= current engineering design decision

These values may be different.

The report shall not automatically copy or promote one level into another.


## 3. Traceability display

When available, a reported engineering parameter shall preserve:

- value
- unit
- origin
- evidence_status
- source_text
- formula_ids
- calculation_record_ids
- note

Missing traceability shall remain missing.

The report shall not invent evidence.

## 4. Geometry semantics

Historical support_length_parameter_m shall be displayed only as:

支护长度参数

It shall not be displayed as:

- 控顶宽度
- 顶梁长度
- 控顶距

Bc remains control_width_m in the working-condition / requirement context.


## 5. Hydraulic component reporting

The report may summarize existing:

- column design
- push-jack design

For column design, eta evidence status must remain visible where input trace
is available.

For push-jack design:

- mt_t94_verified must be preserved
- empty Formula IDs remain empty
- empty Calculation Record IDs remain empty

The report shall not generate missing traceability.

## 6. Future modules

Valve, Pipeline, Pump, Linkage, Structure and Analyses shall show their actual
current status.

NOT_IMPLEMENTED shall remain visible.

The report shall not hide unfinished modules by inventing placeholder
engineering values.

## 7. Calculation boundary

The report implementation must not import or call:

- q_need calculation core
- required-resistance calculation core
- column calculation core
- push-jack calculation core

Its input is OverallSupportDesign only.

## 8. Output

W37-D5 provides:

1. a structured Python summary dictionary
2. a readable Markdown engineering summary

No database persistence is introduced in D5.

No API route is introduced in D5.

No UI implementation is introduced in D5.
