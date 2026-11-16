# Open the NaiviSense Power BI project

1. Install **Power BI Desktop** (Windows). Enable *File > Options > Preview features > Power BI Project (.pbip) save option* and *Store reports using enhanced metadata format (PBIR)* if your version asks.
2. Double-click `NaiviSense_Outcome_Value.pbip`.
3. Home > Transform data > Manage parameters > set **DataFolder** to the absolute path of `../01_Data` (for example `C:\Projects\NaiviSense_BDM_Project\01_Data`). No trailing slash.
4. Close & Apply. All 13 tables load from `01_Data/processed/*.csv`.
5. Open **Model view**: check the star schema (15 relationships; `agg_child_summary` <-> `dim_child` is one-to-one, both directions).
6. Open the **QA Checks** page: every card must equal the value printed in its label (they come from `06_Code/analysis.py`). The league value index must be 1.000.
7. File > Save as .pbix if you need a single file to hand in.

If Desktop reports a schema or TMDL error, note the file named in the message: the project is plain text, so it can be fixed in a text editor (see `NaiviSense_Outcome_Value.Report/definition` and `.SemanticModel/definition`).
Regenerate everything with `python3 ../06_Code/build_pbip.py`.

Mac users: Power BI Desktop is Windows-only. Use a Windows VM, or upload the CSVs to the Power BI Service and rebuild with `DAX_Measures.md`.
