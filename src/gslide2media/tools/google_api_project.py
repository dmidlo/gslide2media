"""
.. module:: google-api-project
   :platform: Unix, Windows
   :synopsis: This Python file contains a class called `ManualSteps` which provides a set of manual
   steps for setting up a Google API project. The class extends the `OrderedDict` class.

Usage:
    - To use this file, create an instance of the `GoogleApiProject` class and call it as a
    function (IIFE with __call__). This will initiate the setup process and guide the user through
    each step. The `run` method will return the path to the client secret JSON file if all steps
    are completed successfully, or `None` otherwise.

.. moduleauthor:: David Midlo dmidlo@gmail.com

This module provides a command-line interface (CLI) to help set up a new Google API project. It
uses various Google APIs to automate the setup process, including the Drive API and Slides API.
The CLI includes several manual steps that the user must follow, such as setting the project name,
enabling API services, and creating OAuth client IDs. These manual steps are organized in a list
of OrderedDict objects, which is defined in the ManualSteps class. The module uses several third-
party libraries, such as InquirerPy and Rich, to provide a user-friendly and visually appealing CLI.

Classes:
    - ``ManualSteps``: This class extends `OrderedDict` and represents a collection of manual steps
        required to set up the Google API project. Each step is defined as a key-value pair, where
        the key is a description of the step and the value is a dictionary containing information
        about the step's completion status and associated functions.
    - ``GoogleApiProject``: This class represents the main entry point for executing the Google API
        project setup. It initializes an instance of `ManualSteps` and provides a `run` method to
        execute the necessary steps.

Example:
.. code-block::python
google_api_project = GoogleApiProject()
client_secret_path = google_api_project.run()
if client_secret_path:
    print(f"Client secret JSON file path: {client_secret_path}")
else:
    print("Google API project setup was not completed.")
"""

from collections import OrderedDict

import webbrowser
from time import sleep
from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import PathValidator

import pyperclip

from rich.progress import track


class ManualSteps(OrderedDict):
    """
    ManualSteps
    ===========

    A class that represents a series of manual steps for setting up a Google Cloud project.

    This class is a subclass of `collections.OrderedDict` that is used to define a series of manual
    steps for setting up a Google Cloud project. Each step is represented by a key-value pair, where
    the key is a string describing the step and the value is a dictionary that contains information
    about the step. The information includes whether the step is complete, a function to execute for
    the step, and any arguments that need to be passed to the function.

    Attributes
    ----------
    project_name : str
        The name of the Google Cloud project.
    project_url : str
        The URL of the Google Cloud Console dashboard for the project.
    cloud_drive_api_url : str
        The URL of the Google Drive API library for the project.
    slides_api_url : str
        The URL of the Google Slides API library for the project.
    consent_screen_wizard_url : str
        The URL of the Create OAuth Client ID wizard for configuring the consent screen.
    oauth_clientid_wizard_url : str
        The URL of the Create OAuth Client ID wizard for creating an OAuth client ID for the project.
    project_credentials_url : str
        The URL of the Google Cloud Console Credentials page for the project.

    Methods
    -------
    __init__()
        Initializes a new instance of the ManualSteps class.
    get_project_name()
        Prompts the user to enter a name for the Google Cloud project.
    verify_project_url()
        Verifies the project URL entered by the user.
    enable_api_services(services: set)
        Enables the specified Google Cloud API services for the project.
    configure_consent_screen()
        Configures the consent screen using the Create OAuth Client ID wizard.
    open_client_id_wizard()
        Opens the Create OAuth Client ID wizard for creating an OAuth client ID for the project.
    client_secret_download_instructions()
        Provides instructions for downloading the Google Auth client secret JSON file.
    import_google_client_secret_json_dialog()
        Prompts the user to import the Google Auth client secret JSON file.
    """
    def __init__(self) -> None:
        super().__init__(self)

        self.update(
            {
                (" Set Project Name.  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.get_project_name,
                    "func_args": {
                        "url": "https://console.cloud.google.com/projectcreate"
                    },
                }
            }
        )
        self.update(
            {
                (" Verify your cloud console Dashboard URL.  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.verify_project_url,
                    "func_args": {},
                }
            }
        )
        self.update(
            {
                (" Enable API services for project.  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.enable_api_services,
                    "func_args": {"services": {"drive", "slides"}},
                }
            }
        )
        self.update(
            {
                (" Configure the Consent Screen Using the Create OAuth Client ID Wizard.  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.configure_consent_screen,
                    "func_args": {},
                }
            }
        )
        self.update(
            {
                (" Create an OAuth Client ID for the project.  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.open_client_id_wizard,
                    "func_args": {},
                }
            }
        )
        self.update(
            {
                (" Download your google auth client_secret json file.  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.client_secret_download_instructions,
                    "func_args": {},
                }
            }
        )
        self.update(
            {
                (" Import client secret Json file  "
                 "(press [enter] to continue.)"): {
                    "complete": False,
                    "func": self.import_google_client_secret_json_dialog,
                    "func_args": {},
                }
            }
        )

    @property
    def project_name(self) -> str:
        """
        Returns the project name.

        :return: The project name.
        :rtype: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name: str) -> None:
        """
        Sets the project name.

        :param project_name: The new project name.
        :type project_name: str
        :return: None.
        """
        self._project_name: str = project_name

    @project_name.deleter
    def project_name(self) -> None:
        """
        Deletes the project name.

        :return: None.
        """
        del self._project_name

    @property
    def project_url(self) -> str:
        """
        Returns the URL of the project dashboard.

        :return: The URL of the project dashboard.
        :rtype: str
        """
        return self._project_url

    @project_url.setter
    def project_url(self, project_name: str) -> None:
        """
        Sets the URL of the project dashboard.

        :param project_name: The name of the project.
        :type project_name: str
        :return: None.
        """
        self._project_url: str = (
            f"https://console.cloud.google.com/home/dashboard?project={project_name}"
        )

    @project_url.deleter
    def project_url(self) -> None:
        """
        Deletes the URL of the project dashboard.

        :return: None.
        """
        del self._project_url

    @property
    def cloud_drive_api_url(self) -> str:
        """
        Returns the URL of the Cloud Drive API.

        :return: The URL of the Cloud Drive API.
        :rtype: str
        """
        return self._cloud_drive_api_url

    @cloud_drive_api_url.setter
    def cloud_drive_api_url(self, project_name: str) -> None:
        """
        Sets the URL of the Cloud Drive API.

        :param project_name: The name of the project.
        :type project_name: str
        :return: None.
        """
        self._cloud_drive_api_url: str = ("https://console.cloud.google.com/apis/library/"
                                          f"drive.googleapis.com?project={project_name}")

    @cloud_drive_api_url.deleter
    def cloud_drive_api_url(self) -> None:
        """
        Deletes the URL of the Cloud Drive API.

        :return: None.
        """
        del self._cloud_drive_api_url

    @property
    def slides_api_url(self) -> str:
        """
        Returns the URL of the Slides API.

        :return: The URL of the Slides API.
        :rtype: str
        """
        return self._slides_api_url

    @slides_api_url.setter
    def slides_api_url(self, project_name: str) -> None:
        """
        Sets the URL of the Slides API.

        :param project_name: The name of the project.
        :type project_name: str
        :return: None.
        """
        self._slides_api_url: str = ("https://console.cloud.google.com/apis/library/"
                                     f"slides.googleapis.com?project={project_name}")

    @slides_api_url.deleter
    def slides_api_url(self) -> None:
        """
        Deletes the URL of the Slides API.

        :return: None.
        """
        del self._slides_api_url

    @property
    def consent_screen_wizard_url(self) -> str:
        """
        Returns the URL of the Consent Screen Wizard.

        :return: The URL of the Consent Screen Wizard.
        :rtype: str
        """
        return self._consent_screen_wizard_url

    @consent_screen_wizard_url.setter
    def consent_screen_wizard_url(self, project_name: str) -> None:
        """
        Sets the URL of the Consent Screen Wizard.

        :param project_name: The name of the project.
        :type project_name: str
        :return: None.
        """
        self._consent_screen_wizard_url: str = ("https://console.cloud.google.com/apis/credentials/"
                                                f"oauthclient?project={project_name}")

    @consent_screen_wizard_url.deleter
    def consent_screen_wizard_url(self) -> None:
        """
        Deletes the URL of the Consent Screen Wizard.

        :return: None.
        """
        del self._consent_screen_wizard_url

    @property
    def oauth_clientid_wizard_url(self) -> str:
        """
        Returns the URL of the OAuth Client ID Wizard.

        :return: The URL of the OAuth Client ID Wizard.
        :rtype: str
        """
        return self._oauth_clientid_wizard_url

    @oauth_clientid_wizard_url.setter
    def oauth_clientid_wizard_url(self, project_name: str) -> None:
        """
        Sets the URL of the OAuth Client ID Wizard.

        :param project_name: The name of the project.
        :type project_name: str

        :return: None.
        """
        self._oauth_clientid_wizard_url: str = ("https://console.cloud.google.com/apis/credentials/"
                                                f"oauthclient?project={project_name}")

    @oauth_clientid_wizard_url.deleter
    def oauth_clientid_wizard_url(self) -> None:
        """
        Deletes the URL of the OAuth Client ID Wizard.

        :return: None.
        """
        del self._oauth_clientid_wizard_url

    @property
    def project_credentials_url(self) -> str:
        """
        Returns the URL of the Google API Project's Credentials Page.

        :return: The URL of the Google API Project's Credentials Page
        :rtype: str
        """
        return self._project_credentials_url

    @project_credentials_url.setter
    def project_credentials_url(self, project_name: str) -> None:
        """
        Sets the URL of the Google API Project's Credentials Page.

        :return: None.
        """
        self._project_credentials_url: str = (
            f"https://console.cloud.google.com/apis/credentials?project={project_name}"
        )

    @project_credentials_url.deleter
    def project_credentials_url(self) -> None:
        """
        Deletes the URL of the Google API Project's Credentials Page.

        :return: None.
        """
        del self._project_credentials_url

    def get_project_name(self, url: str) -> None:
        """
        Display user instructions and prompt the user to choose a name for the Google Cloud project.
        Set the project name and various URLs based on the chosen name.

        :param url: URL for opening the Google Cloud Console's new project wizard page.
        :type url: str
        :return: None
        """

        print(
            """
        ==============================================
        Welcome to the Google API Project Setup Helper
        ==============================================


        The first thing we need to do is create an API Project.

        In order to use programmatic access to google services, For security reasons, Google
        asks that we create and manage projects in the Google Cloud Console.  The cloud console
        helps us manage several api projects for free for private use, and allows us to
        generate the cryptographic bits we need to securely connect to our Google Drive.


        To do that we need to do three things:

            1. Choose a name for your cloud project.
                a. Choose a name that you'll remember and recognize it's purpose.

                b. We recommend using 'gslide2media' and that's the default.
                    but it really can be anything.

            2. Paste/Type your project name in to the Cloud Console's new project wizard.
                a. For your convenience, this tool will copy your project name to the
                    clipboard.
                b. This tool will also open your cloud console's new project wizard page in
                    your default browser.
                    - Be sure to be logged in as the Google account of your preference.

                    The URL this tool will open:
                        https://console.cloud.google.com/projectcreate

            3. Sets your location (if you're part of a Google Workspace Organization)
                    Everyone else, and for personal use, you'll select "No Organization"




    :::User Instructions:::

        """)

        project_name = inquirer.text(
            message="1. Choose a name for your API project [default: gslide2media]",
            default="gslide2media",
            completer={"gslide2media": None},
        ).execute()

        self.project_name = project_name
        self.project_url = project_name
        self.cloud_drive_api_url = project_name
        self.slides_api_url = project_name
        self.consent_screen_wizard_url = project_name
        self.oauth_clientid_wizard_url = project_name
        self.project_credentials_url = project_name

        self.open_new_project_wizard_in_browser(url)

    def open_new_project_wizard_in_browser(self, url: str) -> None:
        """
        Opens the Cloud Console's new project wizard page in the user's default browser.

        :param url: The URL of the new project wizard page.
        :type url: str
        :return: None
        :rtype: None

        :raises: None
        """
        if inquirer.confirm(
            message=f"Open Cloud Console New Project Wizard? ({url}) ([Enter] to Open in Browser)",
            default=True,
        ).execute():
            pyperclip.copy(self.project_name)

            print("""



        :::User Instructions:::


            1. paste {self.project_name} from your clipboard to 'Project Name' in wizard

            2. Select [Browse], and click on [No Organization] (unless you have an org.

            3. Click [Create]

            """)

            sleep(1)
            print(f"\ncopying '{self.project_name}' to clipboard.")
            sleep(1)
            print(f"project_name `{self.project_name}` copied to clipboard.")
            sleep(1)

            for _ in track(range(3), description=f"Opening {url} in default browser."):
                sleep(1)
            webbrowser.open(url)

    def verify_project_url(self) -> None:
        """
        Prints the project URL and asks the user if they want to visit the project dashboard.

        Prints the project URL, which is used to access the project's dashboard on the Google Cloud
        Console. Asks the user if they would like to visit the project dashboard by opening the URL
        in a default web browser.

        :return: None
        """
        print(
            f"""
        Your project `{self.project_name}`'s PROJECT URL:
            - {self.project_url}




    :::User Instructions:::

        1. Would you like to visit your project's dashboard?
            *Not Required

        """)

        if _ := inquirer.confirm(
            message=f"Open {self.project_name} cloud console project dashboard?  ([Enter] to Skip)",
            default=False,
        ).execute():
            for _ in track(
                range(3),
                description="Opening cloud console project dashboard in default browser.",
            ):
                sleep(1)
            webbrowser.open(self.project_url)

    def enable_api_services(self, services: set) -> None:
        """
        Enables API permissions for the required Google services.

        Prints the URLs for the Google Drive API and Google Slides API associated with the project.
        Asks the user if they would like to open the API details pages in a web browser to enable
        the APIs. If the corresponding service is included in the 'services' set, it opens the API
        details page for that service.

        :param services: A set containing the required services to enable.
        :type services: set

        :return: None
        """
        print(
            f"""
        This application requires enabled api permissions to the following google services:

            - Google Drive API
                {self.project_name}'s drive api url:
                        - {self.cloud_drive_api_url}
            - Google Slides API
                {self.project_name}'s slides api url:
                        - {self.slides_api_url}




    :::User Instructions:::

        1. Open each Google Api Settings Page.

        2. Click [Enable] on each Api's settings page.

        """)

        if (
            "drive" in services
            and inquirer.confirm(
                message=(f"Open {self.project_name} Google Drive API Details Page. "
                         "([Enter] to Open in Web Browser.)"),
                default=True,
            ).execute()
        ):
            for _ in track(
                range(3),
                description="Opening Google Drive API Details Page in default browser.",
            ):
                sleep(1)
            webbrowser.open(self.cloud_drive_api_url)

        if (
            "slides" in services
            and inquirer.confirm(
                message=(f"Open {self.project_name} Google Slides API Details Page. "
                         "([Enter] to Open in Web Browser.)"),
                default=True,
            ).execute()
        ):
            for _ in track(
                range(3),
                description="Opening Google Slides API Details Page in default browser.",
            ):
                sleep(1)
            webbrowser.open(self.slides_api_url)

    def configure_consent_screen(self) -> None:
        """
        This method opens the Consent Screen Wizard URL in the user's web browser. Then, it provides
        user instructions for configuring App Information on the OAuth consent screen of
        the Edit App Registration Page.

        :return: None
        """
        if inquirer.confirm(
            message=("Open the Consent Screen Wizard URL. "
                     "([Enter] to Open in Web Browser.)"),
            default=True,
        ).execute():
            pyperclip.copy(self.project_name)

            print("""



        :::User Instructions:::


            1. Click on [Configure Consent Screen] button.

            2. Select [External] on the User Type selection Screen

                a. Click [Create]

            3. Configure App Information on the OAuth consent screen of the Edit App Registration Page.

                a. App Name: {self.project_name}

                b. User Support Email: your gmail address.

                c. App Logo: skip.

                d. App Domain: skip.

                e. Application Home Page: skip.

                f. Application Privacy Policy Link: skip.

                g. Application Terms of Service Link: skip.

                h. Authorized Domains: skip.

                i. Developer Contact Information:

                    i. Email Addresses: your email address.

            4. Click [Save and Continue]

            5. No Scopes need to be defined in the 'Scopes' screen of the Edit App Registration Page.

                a. non-sensitive scopes: No Changes

                b. sensitive scopes: No Changes

                c. restricted scopes: No Changes")

            6. Click [Save and Continue]")

            7. In the 'Test Users' screen of the Edit App Registration Page:")

                a. Click [Add Users]")

                b. Add Your Google Email to the 'Add Users' slide-out.")

                c. Click [Add] in the 'Add Users' slide-out.")

            8. Click [Save and Continue] and review your summary.")

            """)

            sleep(1)
            print(f"\ncopying '{self.project_name}' to clipboard.")
            sleep(1)
            print(f"project_name `{self.project_name}` copied to clipboard.")
            sleep(1)

            for _ in track(
                range(3),
                description="Opening Consent Screen Wizard URL in default browser.",
            ):
                sleep(1)
            webbrowser.open(self.consent_screen_wizard_url)

    def open_client_id_wizard(self) -> None:
        """
        This method opens the Google OAuth Client Id Wizard URL in the user's web browser.
        It provides user instructions for configuring the OAuth Client Id wizard.

        :return: None
        """
        if inquirer.confirm(
            message="Open the Google OAuth Client Id Wizard URL.",
            default=True,
        ).execute():
            pyperclip.copy(f"{self.project_name}_client")

            print("""



        :::User Instructions:::

            1. Set [Application Type] to `Desktop App`.

            2. Set Application [Name] to `{self.project_name}_client`.

            3. Click [Create]

            """)

            sleep(1)
            print(f"\ncopying '{self.project_name}' to clipboard.")
            sleep(1)
            print(f"project_name `{self.project_name}` copied to clipboard.")
            sleep(1)

            for _ in track(
                range(3),
                description="Opening Google OAuth Client Id Wizard URL in default browser.",
            ):
                sleep(1)
            webbrowser.open(self.oauth_clientid_wizard_url)

    def client_secret_download_instructions(self) -> None:
        """
        This method provides instructions to the user for downloading the client secret JSON file
        from the project's credentials page. It also opens the credentials page in the user's web
        browser.

        :return: None
        """
        if inquirer.confirm(
            message=f"Open the project {self.project_name}'s credentials page.",
            default=True,
        ).execute():

            print("""



        :::User Instructions:::

            1. Locate the [OAuth 2.0 Client IDs] section and find the project name's row.

            2. Click on the bold down-arrow [download button] located rightmost
                in the project's row.

            3. In the lower-left of the pop-up, click [Download JSON]")

            4. Save the client secret Json to a known file location")

            """)

            for _ in track(
                range(3),
                description=(f"Opening project {self.project_name}'s credentials "
                             "page URL in default browser."),
            ):
                sleep(1)
            webbrowser.open(self.project_credentials_url)

    def complete_step(self, key) -> None:
        """Mark a specific step as completed.

        :param key: The key of the step to be marked as complete.
        :type key: str
        :return: None
        """
        self[key]["complete"] = True

    def all_complete(self) -> bool:
        """Check whether all steps have been completed.

        :return: True if all steps have been completed, False otherwise.
        :rtype: bool
        """
        bool_set: set[bool] = {True if self[x]["complete"] else False for x in self}

        return bool_set == {True}

    @staticmethod
    def import_google_client_secret_json_dialog():
        """Open a dialog to prompt the user to enter the path to a Google client secret JSON file.

        :return: The path to the selected file.
        :rtype: str
        """
        path_str = inquirer.filepath(
            message="Enter path to your google client secret json file to import:",
            default=str(Path().resolve()),
            validate=PathValidator(is_file=True, message="Input is not a file"),
            only_files=True,
        ).execute()
        Path(path_str).unlink()
        return path_str


class GoogleApiProject:
    """
    Class representing a Google API Project.

    This class encapsulates the functionality to run the necessary steps for setting up
    a Google API project.

    ...

    Attributes
    ----------
    manual_steps : ManualSteps
        An instance of the ManualSteps class that manages the individual steps of the project setup.

    Methods
    -------
    __call__() -> str | Path | None:
        Calls the run() method to start the project setup and returns the path to the client secret
        JSON file if available.

    run() -> str | Path | None:
        Runs the project setup by executing each step until all steps are completed or the user
        interrupts the process. Returns the path to the client secret JSON file if available,
        otherwise returns None.
    """

    def __init__(self):
        self.manual_steps = ManualSteps()

    def __call__(self) -> str | Path | None:
        """
        Calls the run() method to start the project setup and returns the path to the client secret
        JSON file if available.

        :return: The path to the client secret JSON file if available, otherwise returns None.
        :rtype: str | Path | None
        """
        return self.run()

    def run(self) -> str | Path | None:
        """
        Runs the project setup by executing each step until all steps are completed or the user
        interrupts the process.

        Returns the path to the client secret JSON file if available, otherwise returns None.

        :return: The path to the client secret JSON file if available, otherwise returns None.
        :rtype: str | Path | None
        """
        client_secret_path: str | Path | None = None
        while not self.manual_steps.all_complete():
            try:
                steps = [
                    Choice(value=x, name=f"{i + 1}. {x}")
                    for i, x in enumerate(self.manual_steps)
                    if not self.manual_steps[x]["complete"]
                ]

                step_to_complete = inquirer.select(
                    message="", long_instruction="\n[ctrl-c] to exit.", choices=steps[:1]
                ).execute()

                if step_to_complete is None:
                    break

                if step_to_complete == (" Import client secret Json file  "
                                        "(press [enter] to continue.)"):
                    client_secret_path = self.manual_steps[step_to_complete]["func"](
                        **self.manual_steps[step_to_complete]["func_args"]
                    )
                else:
                    self.manual_steps[step_to_complete]["func"](
                        **self.manual_steps[step_to_complete]["func_args"]
                    )

                self.manual_steps.complete_step(step_to_complete)

            except KeyboardInterrupt:
                break
        else:
            return client_secret_path
        return None
