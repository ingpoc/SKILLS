# Apple and GitHub guidance

Checked 2026-07-31. Refresh mutable pricing, roles, workflow features, runner
images, and TestFlight behavior before changing a live account.

## Xcode Cloud

- [Get started and plans](https://developer.apple.com/xcode-cloud/get-started/):
  Apple Developer Program membership currently includes 25 compute hours per
  month; paid tiers require an Account Holder action.
- [Project requirements](https://developer.apple.com/documentation/xcode/setting-up-your-project-to-use-xcode-cloud):
  Xcode Cloud requires a consistent project/workspace, shared schemes,
  automatic signing, and source-control access. Generated projects can make
  onboarding fail and require live proof.
- [Connect GitHub](https://developer.apple.com/documentation/xcode/connecting-xcode-cloud-to-github):
  authorize the Xcode Cloud GitHub App and review its repository permissions.
- [First workflow](https://developer.apple.com/documentation/xcode/configuring-your-first-xcode-cloud-workflow):
  onboarding and source authorization start interactively in Xcode.
- [Custom scripts](https://developer.apple.com/documentation/xcode/writing-custom-build-scripts):
  only the three top-level `ci_scripts` hooks are recognized; scripts cannot
  use `sudo`, and the post-build hook runs even after build failure.
- [Workflow reference](https://developer.apple.com/documentation/xcode/xcode-cloud-workflow-reference):
  start conditions include branches, pull requests, tags, and schedules.
- [Distribution workflow](https://developer.apple.com/documentation/xcode/creating-a-workflow-that-builds-your-app-for-distribution):
  archive destination and clean-build choices affect TestFlight/App Review
  eligibility.
- [TestFlight delivery](https://developer.apple.com/documentation/xcode/distributing-your-xcode-cloud-builds-through-testflight):
  internal-only and external/App Store distribution are different lanes.
- [Build numbers](https://developer.apple.com/documentation/xcode/setting-the-next-build-number-for-xcode-cloud-builds):
  Xcode Cloud assigns increasing integers; existing macOS apps must continue
  above prior build numbers.
- [Usage data](https://developer.apple.com/documentation/xcode/reviewing-xcode-cloud-usage-data/):
  parallel tasks consume aggregate compute, and App Store Connect provides
  usage readback.
- [Cloud-managed certificates](https://developer.apple.com/help/account/certificates/cloud-managed-certificates/):
  Apple manages and rotates cloud distribution certificates subject to team
  roles and signing permissions.

## App Store Connect

- [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/):
  upload must finish processing before a build appears for later actions.
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview):
  processing, groups, review, installation, feedback, and expiry are distinct.
- [App Store Connect API](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-api):
  API access and keys are role-controlled production credentials; they do not
  replace initial Xcode/GitHub onboarding.
- [App records](https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/):
  separate bundle identifiers imply separate app records and independent live
  state.

## GitHub fallback boundaries

- [Included usage](https://docs.github.com/en/billing/reference/product-usage-included)
- [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Deployment protections](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [Self-hosted runner security](https://docs.github.com/en/actions/reference/security/secure-use)

GitHub-hosted macOS is a capped fallback, not a reason to copy signing material
out of Apple. Private-repository protection features and included usage vary by
plan. Self-hosted runners persist between jobs and must not run untrusted code
on a personal workstation containing signing, Keychain, or iCloud data.
