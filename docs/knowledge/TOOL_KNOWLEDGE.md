# PIE-ITR Tool Knowledge

## MammoSuite
- Mobile application used in after-sales/service diagnostic workflows.
- Use for applicable mobile diagnostic/test flows such as Auto Map Run and sensor checks.
- Ultrasonic test guidance: move a fixed obstacle at about 60–70 cm in front of each front ultrasonic sensor and observe readings.
- Shared/public installation/update password: `MMTT`.
- Important distinction: this `MMTT` password is for the MammoSuite installation/update page that asks for a software-install password. It is not the MammoSuite account login password. If a partner asks for a "password", use the screenshot/context to distinguish installer/update password from account credentials before replying.
- Do not instruct an end customer to run MammoSuite; service-tool requests belong to the agent/service-provider side unless explicitly supported otherwise.
- For low vehicle GNSS / satellite-signal cases at the agent/service side, `GNSS Antenna Check` is a high-priority direct diagnostic step. Use its result before defaulting to physical replacement. If abnormal, inspect the rear GNSS antenna disk and connector and use known-good cross-validation where appropriate. If GNSS Antenna Check is normal but the positioning/boundary symptom remains, continue to the next relevant fault domain instead of treating GNSS hardware as confirmed faulty.
- `Connect Checking` screenshots should be interpreted field-by-field rather than as a single pass/fail state. If the Wi-Fi field shows `--`, do not immediately classify it as a Wi-Fi hardware fault. First distinguish between `not currently connected to Wi-Fi` and `Wi-Fi function cannot connect / is not working`. Ask the partner to confirm the actual Wi-Fi behavior before escalating the diagnosis.
- `YUKA mini 2 Vision` supports **Auto Map Run**. Do not infer that the model lacks Auto Map Run capability merely because a workshop attempt is blocked by `not on the lawn`, positioning-mode prompts, indoor conditions, or other test-environment constraints. Separate **model capability** from **current test executability**.
- When a newer software version is available for a repair case with inconsistent test behavior, update first, then repeat **Functional Test**, **Communication Check**, and **Auto Map Run**. Collect all three reports and the **Connect Checking** screenshot. After the tests are complete, upload a fresh log. If one function had failed only in Functional Test but worked in Auto Map Run/manual operation, explicitly ask whether that same item still fails after the software update.
- Real LUBA 2 5000X case: software version `1.30.31.10` was used as the requested update target before repeating the three MammoSuite tests, collecting the Connect Checking screenshot, and uploading a fresh post-test log. The cutting/blade item that had failed only in Functional Test worked normally after the update; treat this as historical version-dependent evidence, not a timeless fixed target version.

## Mammotion Kit
- PC diagnostic tool used in after-sales/service workflows.
- Do not confuse with MammoSuite.
- If an agent is looking for a MammoSuite-only function in the PC tool, identify the wrong tool first.
- Do not instruct an end customer to run Mammotion Kit.
- After replacing a vision module and/or mainboard, if the mower is still not discoverable in the app or via Bluetooth, a high-value service path is: reseat the vision-module connector, connect to Mammotion Kit by cable, run `Flash Name`, ensure **The module firmware versions must be the same.**, then retest Bluetooth. Treat module desynchronization as a supported hypothesis until behavior changes after synchronization.
- If both camera views display normally in Mammotion Kit but FPV fails in the Mammotion App, do not classify the cameras/vision hardware as faulty from the App symptom alone. The wired Kit view proves the camera stream can be produced locally, while App FPV also depends on the network/video-stream/backend path.
- High-value isolation path for `Kit camera OK / App FPV failed` at the agent side: connect the mower to a phone hotspot and retest FPV in the Mammotion App; if it still fails, confirm whether the mainboard or vision module was recently replaced or whether the device name was reflashed, because backend/device-state synchronization may be relevant; if the hotspot test fails and no backend lock/state issue is found, power off the mower, reseat the connectors on both ends of the vision module, and retest.
- For this FPV case, also confirm whether both camera views are unavailable in the App and collect the hotspot-test result. Do not treat `RTK reference station is not ready` as the root cause of FPV failure unless separate evidence links the two.
- If a previously working Mammotion Kit recovery procedure becomes inconsistent after software updates, do not invent a revised procedure from memory or assume the new software is faulty. First collect direct operation evidence from the partner.
- Ask for a short video showing the full workflow from wired mower connection through the relevant `Flash Name` / update step and the exact point where it fails.
- Also collect the current Mammotion Kit software version, a screenshot of module firmware versions, and the exact error message or failure step if one appears.
- Use this evidence to distinguish `tool/version workflow change` from `module synchronization problem`, `device identity mismatch`, or another repair-state issue before giving a new detailed step-by-step procedure.
- When an agent reports that motherboard replacement now causes update or Wi-Fi/Bluetooth problems across multiple units, treat that as potentially reusable tool/process knowledge, but require version-specific and operation-specific evidence before generalizing it into a standard workflow.
- Real LUBA 2 motherboard-replacement support case: after the partner reported that the prior wired Mammotion Kit procedure no longer worked consistently following recent updates, the accepted next action was to request a full operation video, current Mammotion Kit version, module-firmware screenshot, and exact error/failure point before revising the procedure.

## Lark / synchronous remote diagnosis
- Lark video is a valid escalation path when asynchronous email/screenshots/reports are no longer sufficient to understand a complex workshop fault and the agent/service center can operate the machine live.
- Use synchronous video to observe the exact abnormal behavior, guide the next diagnostic step, and reduce repeated back-and-forth when the state is difficult to describe in text.
- PIE remains remote support: PIE observes, asks questions, and gives technical guidance; the agent/service-center personnel perform all physical actions on the mower.
- A video call does not replace decisive evidence that still needs to be retained, such as error codes, test reports, screenshots, logs, measurements, or the validated result of a cross-test.
- Prefer a video session when several interacting hardware symptoms, repeated board failures, uncertain connector/assembly state, or a live test sequence would be materially easier to evaluate together than through another long email exchange.

## LogiQ
- Log-analysis route only for products/cases where capability is supported.
- Unknown model capability must not be assumed.
- Log findings should feed Technical Assessment, Next Action and Reply when they are decisive.

## Capability rule
Maintain tool support by model/product and actor capability rather than assuming every product or person supports every diagnostic path.

## Recording rule
Operational knowledge should be recorded by default when it is useful and not explicitly excluded by the user. Shared/public operational information may be stored here. Credentials, API tokens, private customer data, or other genuinely sensitive secrets remain excluded unless there is an appropriate protected storage location.
