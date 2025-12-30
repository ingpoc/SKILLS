# Browser Testing Examples

Real-world test scenarios with concrete prompts.

## Setup

First, ensure Chrome integration is enabled:
```bash
claude --chrome
# Or in-session: /chrome
```

---

## Example 1: Local Development Testing

**Scenario**: After implementing login form validation

**Prompt**:
```
I just updated the login form validation. Can you:
1. Open localhost:3000/login
2. Try submitting with empty email/password
3. Verify error messages appear
4. Try submitting with invalid email format
5. Confirm format validation works
6. Report any issues
```

**Expected flow**:
- Navigate to localhost:3000/login
- Find submit button, click it
- Check for error messages
- Test with "test@" (invalid email)
- Report findings

---

## Example 2: Console Debugging

**Scenario**: Page has errors on load, need to diagnose

**Prompt**:
```
Open localhost:3000/dashboard and check:
1. Console for ERROR messages on page load
2. Any 404 or 500 errors in network requests
3. Report all errors with context
```

**Expected flow**:
- Navigate to localhost:3000/dashboard
- Read console messages with pattern: `ERROR|404|500`
- Read network requests
- Report findings

---

## Example 3: Form Validation Test Suite

**Scenario**: Comprehensive form validation testing

**Prompt**:
```
Test the registration form at localhost:3000/register:

Test Case 1 - Empty fields:
- Leave all fields empty, click submit
- Verify required field errors appear

Test Case 2 - Invalid email:
- Enter "test@" in email field
- Verify format error appears

Test Case 3 - Password too short:
- Enter "abc" in password field
- Verify min length error appears

Test Case 4 - Valid submission:
- Fill all fields with valid data
- Submit and verify redirect to /welcome

Report results for each test case.
```

---

## Example 4: UI Verification Against Design

**Scenario**: Verify implementation matches Figma mock

**Prompt**:
```
I implemented this login page from a Figma mock. Can you:
1. Open localhost:3000/login
2. Take a screenshot
3. Verify these elements match the design:
   - Email field label is "Email Address"
   - Password field has "Show Password" toggle
   - Submit button is blue and centered
   - "Forgot Password" link below submit button
4. Report any mismatches
```

---

## Example 5: Authenticated App Testing

**Scenario**: Test Google Docs interaction (uses browser login)

**Prompt**:
```
Go to my Google Doc at docs.google.com/document/d/abc123/edit:
1. Read the current content
2. Add this summary at the end:
   "## Summary
   This document covers project progress as of December 2025."
3. Verify the text was added correctly
```

**Works with**: Gmail, Notion, Google Sheets, any site you're logged into

---

## Example 6: Data Extraction

**Scenario**: Scrape product listings

**Prompt**:
```
Go to example.com/products and extract:
1. Product name
2. Price
3. Availability status
4. For all products on the page
5. Save results as products.csv
```

**Expected flow**:
- Navigate to example.com/products
- Read page content
- Extract structured data
- Write CSV file

---

## Example 7: Multi-Tab Workflow

**Scenario**: Compare prices across sites

**Prompt**:
```
1. Open site-a.com/product/123 and note the price
2. Open site-b.com/product/456 and note the price
3. Compare the prices and report which is cheaper
4. Take screenshots of both product pages
```

---

## Example 8: GIF Recording

**Scenario**: Create demo of checkout flow

**Prompt**:
```
Record a GIF showing the complete checkout flow:
1. Start at localhost:3000/cart
2. Click "Proceed to Checkout"
3. Fill in shipping information
4. Click "Place Order"
5. Verify confirmation page appears
6. Save recording as checkout-demo.gif
```

**GIF recording workflow**:
```
1. gif_creator: start_recording
2. [Perform actions]
3. Take screenshot after each action
4. gif_creator: stop_recording
5. gif_creator: export (download=true)
```

---

## Example 9: API Testing

**Scenario**: Verify API calls work correctly

**Prompt**:
```
Test the user profile API:
1. Open localhost:3000/profile
2. Check network requests for the profile API call
3. Verify it returns 200 status
4. Verify response contains user data (name, email)
5. Report any API failures
```

---

## Example 10: Regression Test

**Scenario**: Verify bug fix is still working

**Prompt**:
```
Test the fix for the login redirect bug:
1. Navigate to localhost:3000/login
2. Enter valid credentials
3. Click submit
4. Verify redirect to /dashboard (not stuck on /login)
5. Check console for no errors during redirect
```

---

## Example 11: Form Automation

**Scenario**: Fill form from CSV data

**Prompt**:
```
I have a CSV file with contact data. For each row:
1. Go to crm.example.com/add-contact
2. Click "Add Contact"
3. Fill in:
   - Name from CSV
   - Email from CSV
   - Phone from CSV
4. Click save
5. Wait for success message
6. Continue to next row

Use contacts.csv as the data source.
```

---

## Example 12: Visual Regression

**Scenario**: Compare before/after UI changes

**Prompt**:
```
We just redesigned the settings page. Can you:
1. Open localhost:3000/settings
2. Take a screenshot
3. Verify these changes are present:
   - Dark mode toggle in header
   - New sidebar navigation
   - Settings grouped by category
4. Report any missing elements
```

---

## Example 13: Error Recovery

**Scenario**: Test error handling

**Prompt**:
```
Test error handling for the upload feature:
1. Open localhost:3000/upload
2. Try uploading a non-image file (test.pdf)
3. Verify error message: "Only images allowed"
4. Try uploading a 10MB file
5. Verify error message: "File too large (max 5MB)"
6. Report if errors are handled correctly
```

---

## Example 14: Network Request Analysis

**Scenario**: Debug slow page load

**Prompt**:
```
The dashboard is loading slowly. Can you:
1. Open localhost:3000/dashboard
2. Check network requests
3. Identify which requests take > 1 second
4. Report any failed or slow requests
5. Check console for any related errors
```

---

## Example 15: Cross-Browser Session

**Scenario**: Test with different authentication states

**Prompt**:
```
Test the admin panel:
1. Open localhost:3000/admin while NOT logged in
2. Verify redirect to /login
3. Log in as admin
4. Go back to /admin
5. Verify admin panel loads
6. Check console for no errors
7. Report any authorization issues
```

---

## Evidence Collection Examples

### For tested:true Verification

**Prompt**:
```
Test the checkout feature and collect evidence:
1. Navigate to localhost:3000/checkout
2. Fill form with test data
3. Submit order
4. Collect evidence:
   - Screenshot of confirmation page
   - Console logs (no errors)
   - Network request showing 200 response
5. Save evidence to /tmp/test-evidence/
```

**Evidence saved**:
- `/tmp/test-evidence/confirmation.png`
- `/tmp/test-evidence/console.log`
- `/tmp/test-evidence/network.json`

---

## Troubleshooting Examples

### Issue: Modal Dialog Blocks

**Symptom**: Claude stops responding after clicking a button

**Diagnosis prompt**:
```
I think there's a JavaScript alert blocking the page. Can you:
1. Check if a modal appeared
2. Read the page state
3. Report what's blocking
```

**Solution**: User manually dismisses the alert, then tells Claude to continue.

### Issue: Tab Becomes Unresponsive

**Symptom**: Commands fail on current tab

**Recovery prompt**:
```
The current tab seems stuck. Can you:
1. Create a new tab
2. Navigate to localhost:3000
3. Continue testing from there
```

### Issue: Can't Find Element

**Symptom**: "Could not find element" error

**Debug prompt**:
```
The submit button isn't being found. Can you:
1. Take a screenshot of the page
2. Read the page content
3. Find all buttons on the page
4. Identify the correct submit button
```

---

## Prompt Best Practices

### DO ✅

```
- "Navigate to localhost:3000"
- "Check console for ERROR messages"
- "Take a screenshot to verify"
- "Report any issues found"
- "Filter console logs for 'api' pattern"
```

### DON'T ❌

```
- "Read all console logs" (too verbose)
- "Click the button with ID submit-btn-12345" (fragile)
- "Open the URL and do everything" (ambiguous)
- "Test the page" (too vague)
```

---

## Quick Prompt Templates

Copy and adapt these templates:

### Smoke Test
```
Navigate to {URL}, check console for errors, take screenshot, report status.
```

### Form Test
```
Go to {URL}, find {form} form, test with {data}, verify {expected_result}.
```

### Console Debug
```
Open {URL}, trigger {action}, check console for {pattern} messages.
```

### Regression Test
```
Test fix for {bug}: Go to {URL}, perform {steps}, verify {expected}.
```

### Data Extraction
```
Navigate to {URL}, extract {fields}, save as {filename}.{format}.
```

### GIF Recording
```
Record GIF of {workflow}: Start at {URL}, perform {actions}, save as {name}.gif.
```
