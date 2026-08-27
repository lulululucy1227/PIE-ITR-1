# PIE-ITR Tool Knowledge

## MammoSuite
- Mobile application used in after-sales/service diagnostic workflows.
- Use for applicable mobile diagnostic/test flows such as Auto Map Run and sensor checks.
- Ultrasonic test guidance: move a fixed obstacle at about 60–70 cm in front of each front ultrasonic sensor and observe readings.
- Shared/public download password: `MMTT`.
- Do not instruct an end customer to run MammoSuite; service-tool requests belong to the agent/service-provider side unless explicitly supported otherwise.
- For low vehicle GNSS / satellite-signal cases at the agent/service side, `GNSS Antenna Check` is a high-priority direct diagnostic step. Use its result before defaulting to physical replacement. If abnormal, inspect the rear GNSS antenna disk and connector and use known-good cross-validation where appropriate. If GNSS Antenna Check is normal but the positioning/boundary symptom remains, continue to the next relevant fault domain instead of treating GNSS hardware as confirmed faulty.

## Mammotion Kit
- PC diagnostic tool used in after-sales/service workflows.
- Do not confuse with MammoSuite.
- If an agent is looking for a MammoSuite-only function in the PC tool, identify the wrong tool first.
- Do not instruct an end customer to run Mammotion Kit.
- After replacing a vision module and/or mainboard, if the mower is still not discoverable in the app or via Bluetooth, a high-value service path is: reseat the vision-module connector, connect to Mammotion Kit by cable, run `Flash Name`, ensure **The module firmware versions must be the same.**, then retest Bluetooth. Treat module desynchronization as a supported hypothesis until behavior changes after synchronization.

## LogiQ
- Log-analysis route only for products/cases where capability is supported.
- Unknown model capability must not be assumed.
- Log findings should feed Technical Assessment, Next Action and Reply when they are decisive.

## Capability rule
Maintain tool support by model/product and actor capability rather than assuming every product or person supports every diagnostic path.

## Recording rule
Operational knowledge should be recorded by default when it is useful and not explicitly excluded by the user. Shared/public operational information may be stored here. Credentials, API tokens, private customer data, or other genuinely sensitive secrets remain excluded unless there is an appropriate protected storage location.