## Obtain testing data from FP

curl -H "Authorization: Bearer ..." https://fernportal.xtherma.de/api/device/FP-XX-XXXXXX

Some tests expect a specific order and some specific values.


## Snapshot testing

Several tests are based on snapshots in which the expected test results are stored. If the test results change, the corresponding tests will fail. In this case, the snapshots need to be updated again.
To update a snapshot, run the test with the `--snapshot-update` flag, e.g.
```
pytest tests/test_sensor.py --snapshot-update
```
When the test is run again (without the update flag), it compares the results to the stored snapshot, and all checks should pass.

**Warning:** Before updating the snapshot, make sure the code is working correctly - otherwise, you might end up saving incorrect results!
