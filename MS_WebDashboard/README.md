# Smart IoT Bolt Dashboard

A web-based dashboard for monitoring industrial pipelines equipped with Smart IoT Bolts that provide real-time temperature and pressure data.

## Project Overview

This dashboard provides a modern interface for monitoring and managing industrial pipeline systems. It includes real-time visualization of sensor data, alerts management, and system configuration.

### Features

- **Real-time Monitoring**: Track temperature and pressure readings from smart bolts
- **Interactive 3D Pipeline Visualization**: View your entire pipeline system in 3D with color-coded status indicators
- **Alert Management**: Receive and manage alerts when sensor readings exceed thresholds
- **Sensor Management**: Configure and monitor the status of individual sensors
- **User Authentication**: Secure login system with session management
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Project Structure

```
MS_WebDashboard/
├── assets/                # Static assets
│   └── img/               # Images and icons
├── css/                   # Stylesheets
│   ├── dashboard.css      # Dashboard-specific styles
│   ├── landing.css        # Landing page styles
│   ├── login.css          # Login page styles
│   └── style.css          # Global styles
├── js/                    # JavaScript files
│   ├── auth.js            # Authentication functionality
│   ├── charts.js          # Chart generation and updates
│   ├── dashboard.js       # Dashboard functionality
│   ├── main.js            # Shared functionality
│   └── pipeline-3d.js     # 3D pipeline visualization
├── dashboard.html         # Dashboard page
├── index.html             # Landing page
├── login.html             # Login page
└── README.md              # Project documentation
```

## Setup and Usage

This is a client-side application that uses modern JavaScript and CSS. It can be run locally or deployed to a web server.

### Prerequisites

- Modern web browser with JavaScript enabled
- Internet connection (for loading CDN resources)

### Running Locally

1. Clone or download this repository
2. Open `index.html` in your web browser
3. For the login page, use any username with at least 3 characters and password with at least 6 characters

### Demo Credentials

For demonstration purposes, you can use the following credentials:
- Username: admin
- Password: admin123

*Note: In a production environment, you would integrate this with a proper backend authentication system.*

## Development Notes

### Technologies Used

- HTML5, CSS3, and JavaScript (ES6+)
- Chart.js for data visualization
- Three.js for 3D pipeline rendering
- GSAP for animations
- Font Awesome for icons

### External Dependencies

The project uses the following external libraries loaded from CDNs:
- Chart.js
- Three.js
- GSAP (GreenSock Animation Platform)
- Font Awesome

### Extending the Dashboard

To add new functionality:
1. Create new section in `dashboard.html`
2. Add corresponding styles in `dashboard.css`
3. Implement functionality in the appropriate JavaScript file

## Future Enhancements

- Integration with actual IoT API endpoints
- Real-time data using WebSockets
- User management system
- Historical data analysis
- Export functionality for reports
- Dark mode theme option

## License

This project is for demonstration purposes only. 