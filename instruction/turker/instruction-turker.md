---
# Pandoc
title: MTurk Instruction - Turker
author: Jiahao Zhang
date: Mar. 1, 2022
documentclass: article
papersize: a4
geometry: margin=2.5cm
mainfont: Calibri
sansfont: Calibri
monofont: JetBrains Mono
fontsize: 11pt
listings: true
toc: true
linkcolor: Cyan
filecolor: Cyan
citecolor: Cyan
urlcolor: Cyan
# Eisvogel
titlepage: true
logo: img/davidz.png
header-right: Jiahao Zhang
toc-own-page: true
table-use-row-colors: false
listings-no-page-break: false
code-block-font-size: \normalsize
footer-left: "\\footerlogo"
header-includes:
  - |
    ```{=latex}
    \newcommand{\footerlogo}{\includegraphics[width=2cm]{img/anu.png}}
    ```
# Crossref
subfigGrid: true
autoSectionLabels: true
---

> Issues related to Vidat, please create issues [here](https://github.com/anucvml/vidat/issues).

# Sign In or Create an Account

[MTurk Worker Sandbox](https://workersandbox.mturk.com/)

> You may be required to fill a registration form if you are the first time to use MTurk.

![Worker registration](img/worker-registration.png)

# Find Our Hit

![Search for _**IKEA Assembly Instruction Video Segmentation**_ and Accept.](img/step1-1.png)

![Expand to read the instruction.](img/step1-2.png)

![Open the link in a new tab.](img/step1-3.png)

# Annotation In Vidat

## Steps

#### Step 1

![Click the thumbnail to open the step preview.](img/step3-1.png)

#### Step 2

![Locate left and right panel to align start and end frame.](img/step3-2.png)

#### Step 3

![Click the second button on the corresponding row to set start and end time for this segment. Or the same button on the step preview.](img/step3-3.png)

![Once the duration is longer than 0, the warning (yellow) color will disappear.](img/step3-4.png)

#### Step 4

![Delete the segment if it is not shown in the video.](img/step3-5.png)

#### Step 5

![Open the side menu after finishing annotation, and click submit button](img/step3-6.png)

> Please check the followings before submitting
>
> - the video is not changed
> - the configuration is not changed
> - duration of each action is greater than 0

![Your submission id will be notified and copied to your clipboard automatically.](img/step3-7.png)

## Vidat Introduction

![**Header** a video caching status and a dark mode toggle. Once all frames are cached, you can change the frame smoothly.](img/step2-1.png)

> some useful hot keys for video control:
>
> - `P` play / pause video segment

![**Keyframe Panel** on the left, you can play the video segment specified by the range or edit keyframe list. In the middle, you can change the frame of left/right panel by dragging the left/right thumb or the range, the purple below indicates the frames annotated by actions. One the right, you can quick locate the keyframe(s).](img/step2-2.png)

> Some useful hot keys for frames control:
>
> - `COMMA, <`, `PERIOD, >` advance to previous / next keyframe
> - `LEFT-ARROW`, `RIGHT-ARROW` previous / next frame
> - `UP-ARROW`, `DOWN-ARROW` cycle through the frame slider: right > range > left
> - `PAGE-UP`, `PAGE-DOWN`, jump to previous / next 10% of video

![**Left/Right Canvas Panel and Control Panel (in the middle)** there is an action indicator on the left-bottom corner to show actions which cover current frame.](img/step2-3.png)

![**Action / Video Segment Table** you can modify the action annotaion List.](img/step2-4.png)

> - `ADD` or press `PLUS (+)` key on your keyboard to add a new action
> - `CLEAR` bulk delete all actions
> - `start` start time in seconds
> - `end` end time in seconds
> - `duration` duration (end time - start time) in seconds
> - `action` the action label, in this task, it refers to steps
> - `object` the corresponding object label, please leave it as default in this task
> - `description`
> - ![locate](img/gps_fixed_black_24dp.svg) set start/end time as current left/right frame
> - ![edit](img/edit_location_alt_black_24dp.svg) set current left/right frame as start/end time
> - ![delete](img/delete_black_24dp.svg) delete this action

# Submit In MTurk

![Paste the submission id and click submit.](img/step4-1.png)

> Thanks for your cooperation, cheers!
