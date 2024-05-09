---
pip: 12
title: Automated Version Updates and Announcements in GUI and Daemon Client
author: Javad Rajabzadeh <ja7ad@live.com>
status: Rejected
type: Standards Track
category: Interface
created: 2023-11-26
---

## Abstract

This proposal suggests an enhancement to both the graphical user interface (GUI) and command-line interface (CLI) clients of our blockchain application. The objective is to implement an automated version-checking mechanism that will discreetly run in the background for the GUI client and precede the execution of the CLI client. For the GUI, a scheduled task will periodically check for updates, and if a new version is detected, a non-intrusive announcement popup will be displayed, providing users with the option to update or cancel. On the CLI side, before initiating the node, a version check will be performed, and if a new version is available, detailed update information, including version number, change logs, and a prompt for user confirmation, will be presented. These improvements aim to streamline the update process, ensuring users are informed promptly and can seamlessly incorporate the latest enhancements to the blockchain application.

## Motivation

The motivation behind proposing these updates to both the graphical user interface (GUI) and command-line interface (CLI) clients of our blockchain application stems from a commitment to providing users with a more streamlined and user-friendly experience. Keeping our software up-to-date is paramount for security, feature enhancements, and bug fixes. The current lack of an automated version-checking mechanism in both the GUI and CLI clients creates a potential gap in user awareness and hinders the adoption of the latest improvements.


## Specification

For the GUI client, users may not be promptly informed about available updates, leading to a delay in accessing new features or crucial security patches. The proposed periodic version checks with a discreet announcement popup ensure that users are promptly notified of updates, empowering them to make informed decisions on whether to update or continue with the existing version.

Similarly, for the CLI client, incorporating a version-checking step before the node execution ensures that users are aware of new releases and can choose to update based on detailed information provided. This proactive approach not only enhances user experience but also facilitates a smoother transition to newer versions.

In summary, these proposed enhancements aim to fortify user engagement, security, and overall satisfaction by implementing a robust and automated version-checking mechanism in both the GUI and CLI clients of our blockchain application.


### 1. GitHub Release API Integration:

- **Endpoint:** Utilize the GitHub Release API to check for the latest version of the blockchain application.
- **API Endpoint:** [GitHub Release API](https://api.github.com/repos/pactus-project/pactus/releases/latest)
- **Data Obtained:**
   - **Version:** Extract the version number from the API response.
   - **Title:** Retrieve the title of the release for informative purposes.
   - **Description (Changelog):** Capture the description of changes for detailed information.

### 2. Local JSON File Integration:

   File Location: The version information will also be checked locally from a JSON file located in the project root.
   JSON File Format:

```json
{
  "title": "foobar",
  "version": "1.17.0",
  "description": "foobar",
  "changes": {
    "add":["foo", "bar"],
    "fix":["foo"],
    "refactor":["bar"],
    "chore":[]
  }
}
```

- **Data Obtained:**
    - **Version:** Extract the version number from the local JSON file.
    - **Title:** Retrieve the title of the release from the JSON file.
    - **Description (Changelog):** Capture the description of changes from the JSON file.
