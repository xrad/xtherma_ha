<h2 align="center">
   <a href="https://www.xtherma.de/">Xtherma</a> Heatpump integration for <a href="https://www.home-assistant.io">Home Assistant</a>
   </br></br>
</h2>

## Installation (HACS)

1. Go to your Home Assistant > HACS management page.
2. Open the three-dot menu and select `User defined repositories`
3. In the repository field, add `https://github.com/Xtherma/xtherma_ha` and select type `Integration`
4. Click `Add`

After that, you can search and download  the Xtherma integration. Once downloaded within HACS, you will be able to add it via Home Assistant's **Settings > Devices & Services > Add Integration**.

## Installation (manual)

Copy the folder `custom_components/xtherma_fp` into the HA installation so that it can be found under `/config/custom_components/xtherma_fp`.
Then restart Home Assistant.

## Configuration

In **Settings > Devices & Services**, click on **Add Integration**. The configuration dialog will ask for the REST API token and the serial number.

Both can be copied from the remote portal (Start page -> My Account).

## Function

Currently, the REST API is read-only. Only the sensor values from the `telemetry` data section are displayed.

## Logging

Debug logs can be enabled as follows:

```yaml
logger:
  default: info
  logs:
    custom_components.xtherma_fp: debug
```
