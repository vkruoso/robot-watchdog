

*** Test Cases ***

Testing
    Log  Testing

UTF-8 Test
    Log  this is a test with áccents
    Sleep  1s

This should fail
    Fail  error message

