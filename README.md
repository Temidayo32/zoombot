# Installation Guide for Meeting Bot

## Step 1. Create a Zoom General App

To get started, you'll need to create a Zoom Generic App to obtain the necessary credentials for authentication.

1. **Sign in to the Zoom App Marketplace**: Go to the [Zoom App Marketplace](https://marketplace.zoom.us/) and log in with your Zoom account.

2. **Create a New App**:
   - Click on **Develop** in the top menu, then select **Build App**.
   - Choose **General App** for the app type.

3. **App Credentials**:
   - Fill in the **Basic Information** fields such as App Name, Short Description, and Long Description.
   - **Redirect URL for OAuth**: Use `http://localhost:5000/callback` as your redirect URL.

4. **Obtain Client ID and Client Secret**:
   - Once your app is created, you'll be redirected to the app settings page.
   - Here, you'll find your **Client ID** and **Client Secret**. Keep these safe, as you'll need them for authentication.

5. **Authorization URI**:
   - The authorization URI for Zoom OAuth is usually in the following format:
     ```
     https://zoom.us/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:5000/callback
     ```
6. **Create a `.env` File**: Store your Zoom app credentials in a `.env` file:

   ```plaintext
   clientID=your_client_id_here
   clientSecret=your_client_secret_here
   authURI=authorization-uri-goes-here
   ```

## Step 2: Install Required Linux Packages

To run the Meeting Bot, you will need to install specific Linux packages. These packages are essential for the functionality of certain Python libraries used in the bot. To install the necessary packages, locate the `install_packages.sh` script included in the project. Run this script to automatically install all required dependencies.

### Execute the Installation Script

1. **Make the Script Executable:**
   Open your terminal and run:
   ```bash
   chmod +x install_packages.sh
   ```

2. **Run the Script:**
   Execute the installation script by running:
   ```bash
   ./install_packages.sh
   ```

## Step 3: Install Python Dependencies
After installing the necessary Linux packages, you'll need to install the Python dependencies specified in the requirements.txt file.

Run the following command:

```bash
pip install -r requirements.txt
```

## Step 4: Verify Sound Devices

After installing the required packages, you can check for available sound devices that can be used for recording.

Run the following command to execute the sound device query:
```bash
python query.py
```

This will provide you with a list of available sound devices for the Meeting Bot.

## Conclusion

Once you have installed the necessary packages and verified your sound devices, the Meeting Bot should be ready for use. If you encounter any issues, please let me know. Thanks.
