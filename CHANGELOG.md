# Changelog

<!--next-version-placeholder-->


## v1.0.0 (14/01/2026)

### New Version

 - Renamed Modules and Classes for better readability.
 - Added callback functions in protocol to be used as a hook. Either by overriding
   or monkey patching.
 - New wait and timeout handling in WaitForResponse.
 - Now Creating api by private factory class from Enum with WaitForResponse and SubmitTask class.
 - Added methods for action instead of callable instances.

### Test
 - Added tests to all package modules.

## v0.3.0 (20/02/2025)

### Feature

- Add method for observer class to insert subscriber at first position of observer list.

- Create an observer for send method. Which is called when data is sent

### Documentation

- Add documentation for new Feature.
- Add example usage in documentation.


## v0.2.0 (15/01/2025)

### Feature

- Rename same objects for better understanding

- Add possibility to send instance order or order given as argument when calling instance of `GiveOrder` class.

- Remove `_Advanced_Command` and `_Advanced_Wait` class for better readability.

### Documentation

- Add documentation for new Feature.
- Remove obsolete documentation.
- Fixed some typos in docstrings.


## v0.1.0 (19/11/2024)

- First release of `imcntr`!
