# gslide2media
Python app that uses the Google Slides API and the Google Drive API to download a Google Slides presentation as an mp4, svg, png, jpeg,


```python
# folder_id = "0B1M-9VPKe8ZnU0phUmFYNkNOaEU"
# folder = Folder(folder_id=folder_id)
# folder.recursive_save(set(ExportFormats))

# presentation_id = "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ"
# presentation = Presentation(presentation_id=presentation_id)
# presentation.save(set(ExportFormats))

# root_folder = Folder()
# for _ in root_folder.presentations.get():
#     print(_)

presentation_ids = [
    "1oenPoz35QxrfrSrHeLR-NN5EDI3Nr5UuTbhOID02DsQ",
    "19cm7dFMa7SLCp0DdD8skOpEbLa8dO3QUB9r0vhzTcXA",
]
folder_ids = [
    "1OotVomGB-_HvkgPO6nRQeJ5qQjR1yI-c",
    "0B7N3Xy--o-kQNkh0VkxKWVZueE0",
    "0B2uMDReI2FI0SlNKb3FZQmQxZWs",
    "0B7N3Xy--o-kQfkh5aV9iMnRic0lTeE1mS2x4MUFmc0xxekV5amVhMTY4RkUxYmRYWnZjclU",
]
custom_presentation_name = "hello_gen_pres"
custom_presentation_ids = [
    ("1odV-0NE1J1h9IBuh_t2lRY8n_-84fwJZOWwzRtddOtc", "g3fd1e2d0d3_2_18"),
    ("1u0En6FFIQjmySLo0PxSdnm-gDkwFG6XH2VvCfJZ5V00", "p"),
    ("1Me_TyonOhtFjHkP7Ju-kjdAPI4-kFqfoTxLzE_rtELE", "g1cb6702d99_1_0"),
]
custom_presentation = Presentation(
    presentation_id=custom_presentation_name,
    presentation_name=custom_presentation_name,
    parent="batch",
    slide_ids=custom_presentation_ids,
    is_batch=True,
)

# folder_list_of_folds = Folder(presentations=[custom_presentation])
# folder_list_of_folds = Folder(folder_ids=folder_ids)
# folder_list_of_folds = Folder(presentation_ids=presentation_ids)
# folder_list_of_folds = Folder(presentations=[custom_presentation], folder_ids=folder_ids)
# folder_list_of_folds = Folder(presentations=[custom_presentation], presentation_ids=presentation_ids)
# folder_list_of_folds = Folder(folder_ids=folder_ids, presentation_ids=presentation_ids)
folder_list_of_folds = Folder(
    presentations=[custom_presentation],
    folder_ids=folder_ids,
    presentation_ids=presentation_ids,
)
files = folder_list_of_folds.recursive_to_file({"mp4"})

for to_file in files:
    for _ in to_file:
        print(_)

# folder_list_of_presentations = Folder(presentation_ids=presentation_ids)

# folder_list_of_presentations.save(set(ExportFormats))

# custom_presentation.save({"svg", "png", "jpeg", "json", "mp4"})
```
