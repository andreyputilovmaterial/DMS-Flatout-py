# map-flatout-prefill
Python script that helps you pre-fill flatout map.

Download files from the latest Release page:
[Releases](../../releases/latest)

To get it started, just edit the BAT file and insert the name of your map.

If you need to repeat the structure of AA-generated SPSS, apply AA on your MDD now.

Then, start the BAT file. As a result, it will generate:
`mdd_map_R123456.xlsx_filled_with_script.xlsx`
in the same directory. Just grab contents from columns AI-AN ("variables" sheet) and grab analysis values from columns M-Q on "cats by vars" sheet.

Enjoy

Please note, there is no "pause" at the end. If it disappears, it means everything worked and finished successfully.

I tested it on a couple of projects, worked well.

You need python installed and IBM/Unicom Professional to have this tool running. It is a requirement.

If some python packages are missing, just type
`python -m pip install xxx`
where xxx is a missing package.

