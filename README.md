# gslide2media
Python app that uses the Google Slides API and the Google Drive API to download a Google Slides presentation as an mp4, png, jpeg, 

## Upcoming Features

- Implement Options History for easier CLI ux.
  - add "set-label" to all creational parsers
  - add "history <label>"
  - add "history remove <Optional<label>>
  - add "history clear" (w/ confirm)
- Add --options-set option to "interactive" prompt.
- Remove _from_api and replace with _options_source.
- Implement strategy pattern for validators and modifiers.
- add "auth reauth" and "auth clear" (confirm for clear)
- Async operations when working with a presentation.
- Multi-process operations when working with a set of presentations.
- Import Options YAML to facilitate CRON/Task Scheduler scheduling.
- add import client secret option for _from_api users
- Add list of preconfigured display types (Fuzzy Search)
  - https://en.wikipedia.org/wiki/Comparison_of_high-definition_smartphone_displays#Full_list
  - https://en.wikipedia.org/wiki/Display_resolution#Common_display_resolutions
  - https://en.wikipedia.org/wiki/List_of_common_resolutions
  - https://en.wikipedia.org/wiki/High-definition_television#Display_resolutions
  - https://en.wikipedia.org/wiki/VC-1
  - https://en.wikipedia.org/wiki/Ultrawide_formats
  - https://en.wikipedia.org/wiki/Computer_display_standard
  - https://en.wikipedia.org/wiki/Graphics_display_resolution
  - CLI Fuzzy: https://inquirerpy.readthedocs.io/en/latest/pages/prompts/fuzzy.html
- Integration with platform specific secure key stores (MacOS Keychain, Windows Credential Locker, Gnome Freedesktop Secret Service, KDE4 & KDE5 KWallet) via keyring.
- Create home for Errors/Exceptions
- add logging
- Compositing Support
  - Support for embedded video.
    - When a slide has an embedded video (YouTube, or Drive File):
      - determine the embed's position and scale in the slide
        - relate json objects to svg elements.
      - download the video (could be mp4, fmp4, or hsl)
      - determine FPS of video
      - remove or duplicate video frames to match config's FPS
      - determine length of video in seconds
      - adjust slide duration according to length of video in seconds.
    - https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.composite
    - https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.pad
  - Support for slide object transforms
    - Transition and Motion/Animation support
      - https://developers.google.com/slides/api/guides/transform
      - https://developers.google.com/slides/api/concepts/transforms
- Export as self-contained web-page.
  - Generate "Publish to Web" URL via google drive.
  - Save as MHTML, Mozilla Archive Format (MAF), or Zip with Data URIs,
- Add composable audio tracks per slide.
  - Detect if a slide already has an embedded audio track.
- Implement a bidirectional stream gRPC server w/ protobuffs as CLI command 'gslide2media server start` (along with expected configurable options {host,port, etc..})
  - for mp4s use fmp4, or hls
    - Consider alternatives:
      - https://en.wikipedia.org/wiki/High-definition_video#HD_on_the_World_Wide_Web/HD_streaming
      - https://www.wowza.com/blog/video-codecs-encoding
      - https://www.wowza.com/blog/encoding-vs-transcoding
      - https://www.wowza.com/blog/h266-codec-versatile-video-coding-vvc-explained
      - https://www.wowza.com/blog/vp9-codec-googles-open-source-technology-explained
      - https://www.wowza.com/blog/av1-codec-aomedia-video-1-explained
      - https://www.wowza.com/blog/h265-codec-high-efficiency-video-coding-hevc-explained
      - https://www.wowza.com/blog/h264-codec-advanced-video-coding-avc-explained
  - for other files, fragment files for transport wherever possible.
- Implement a Node bidirectional stream gRPC w/ protobuffs client library in Typescript. npm -i gslide2media-client
  - Once this is done, complete writing all pytest/hypothesis unit tests.
  - Write integration tests for gslide2media server <-> gslide2media-client
- Implement an Electron front end. npm -i gslide2media-gui, and a `gslide2media gui` CLI
- Bundling
  - bundle for python users
    - bundle gslide2media as wheel for PyPI
      - Use MANIFEST.in to include front-end bundle (gslide2media-gui)
        - https://www.turing.com/kb/7-ways-to-include-non-python-files-into-python-package
      - MacOS Intel/ARM
      - Windows Intel/ARM
      - ManyLinux Intel/ARM
    - bundle for conda - Intel/ARM
    - bundle for Google Cloud Artifact Registry
  - bundle for JS/TS users
    - npm
    - yarn
    - pnpm
  - bundle as standalone
    - git tags, github releases
    - exe - Intel/ARM
    - .app - Intel/ARM
      - Signing and notarizing an Electron app
        - https://til.simonwillison.net/electron/sign-notarize-electron-macos
    - .deb - Intel/ARM
    - .rpm - Intel/ARM
    - REFS:
      - https://github.com/indygreg/python-build-standalone
      - https://til.simonwillison.net/electron/python-inside-electron
      - https://github.com/Nuitka/Nuitka
      - PyInstaller
      - py2exe
      - py2app
      - https://imageio.readthedocs.io/en/stable/user_guide/freezing.html
- Deployment
  - Deploy for MacOS users
    - Homebrew
    - MacPorts
    - Mac App Store?
  - bundle for Powershell
    - remeber that Powershell runs on all platforms...
    - bundle for Chocolatey
    - bundle for Windows Package Manager (winget)
    - bundle for scoop
    - bundle for Nuget


## Completed

- ~~Write a Hash function for Options object.~~
## Enabling Google Drive and Slides APIs and getting a `client_secret` **json** file.


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
