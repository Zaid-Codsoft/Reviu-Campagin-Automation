# Reviu.pk - Professional Lead Generation System

A comprehensive, professional lead generation and email outreach system built with Python Flask, designed specifically for Pakistani businesses.

## 🚀 Features

### **Intelligent Business Collection**
- **15 Professional Categories** with intelligent business matching
- **Related Business Types** - Each category includes similar business types
- **Verified Business Database** with real Pakistani companies
- **Smart Lead Generation** that combines verified data with intelligent generation
- **Email Validation** during lead collection to ensure deliverability

### **Professional Email Generation**
- **Google Gemini 2.5 Pro** integration for high-quality email generation
- **Personalized Content** based on business type and location
- **Professional Templates** with your company information
- **Fallback System** for reliable email generation

### **Automated Email Campaigns**
- **SMTP SSL Support** for secure email delivery
- **Bulk Email Sending** with rate limiting
- **Campaign Tracking** with detailed results
- **Success Rate Monitoring** for campaign optimization

### **Data Management**
- **CSV Storage** for leads, emails, and results
- **Historical Records** for duplicate prevention
- **Campaign Statistics** and analytics
- **Session Management** with data persistence

## 🖥️ Dashboard Overview

The Reviu.pk Lead Generation System features a modern, intuitive web dashboard that provides complete control over your lead generation and email outreach campaigns.

### **Lead Generation Interface**
- **Smart Input Form**: Select business category (e.g., "Technology"), city (e.g., "Karachi"), and target count
- **One-Click Generation**: Generate leads with a single button click
- **Real-time Processing**: Watch as the system collects and validates business data

### **Performance Dashboard**
- **Key Metrics Display**: 
  - Leads Generated (with count)
  - Emails Created (with count)
  - Emails Sent (with count)
  - Success Rate (percentage)
- **Action Buttons**: Generate Emails, Send Emails, Validate Emails, Reset Session

### **Data Management Tables**
1. **Generated Leads Table**: Shows business name, category, city, and email for all collected leads
2. **Generated Emails Table**: Displays email status and preview options for each lead
3. **Email Campaign Results**: Tracks delivery status, messages, and timestamps for all sent emails

### **User Experience Features**
- **Clean, Modern Design**: Purple gradient header with white content cards
- **Responsive Layout**: Optimized for desktop and mobile devices
- **Real-time Updates**: Live data refresh and status updates
- **Professional Icons**: Intuitive visual indicators for all functions

### **Dashboard Screenshot**
![Reviu.pk Lead Generation System Dashboard](https://raw.githubusercontent.com/Zaid-Codsoft/Reviu-Campagin-Automation/master/Screenshot_23-8-2025_233954_127.0.0.1.jpeg)

*The dashboard shows the complete lead generation workflow with real-time metrics, data tables, and action controls.*

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App      │    │   Data Layer    │
│   (HTML/JS)     │◄──►│   (API Routes)   │◄──►│   (CSV/JSON)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Core Modules   │
                    │                  │
                    │ • Business       │
                    │   Collector      │
                    │ • Email          │
                    │   Generator      │
                    │ • Email Sender   │
                    │ • Data Manager   │
                    └──────────────────┘
```

## 📋 Requirements

- Python 3.8+
- Flask 2.3.3
- Google Generative AI (Gemini)
- SMTP email server access
- Required Python packages (see requirements.txt)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Trustpk-email-Automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```env
   
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web interface**
   Open your browser and go to: `http://localhost:5000`

## 🎯 Usage

### **1. Generate Leads**
- Select a business category (e.g., "Technology")
- Choose a city (e.g., "Karachi")
- Set target lead count (10-500)
- Click "Generate Leads"

The system will:
- Collect verified businesses from the database
- Generate related business types (Software Company, IT Company, etc.)
- Create additional businesses to reach target count
- Validate email addresses for deliverability

### **2. Generate Emails**
- After leads are generated, click "Generate Emails"
- The system uses Gemini AI to create personalized emails
- Each email includes your company information and registration link

### **3. Send Campaign**
- Review generated emails
- Click "Send Emails" to start the campaign
- Monitor progress and results in real-time

## 📊 Business Categories

The system includes **15 professional categories**:

1. **Technology** - Software, IT, Web Development, AI/ML
2. **Marketing & Advertising** - Digital Marketing, SEO, Branding
3. **Food & Hospitality** - Restaurants, Hotels, Tourism
4. **Healthcare & Medical** - Hospitals, Clinics, Wellness
5. **Education & Training** - Schools, Universities, Training
6. **Real Estate & Construction** - Property, Architecture, Building
7. **Automotive & Transport** - Cars, Logistics, Supply Chain
8. **Banking & Finance** - Banks, Insurance, Investment
9. **Legal & Professional Services** - Law Firms, Consulting
10. **Retail & Shopping** - Fashion, Electronics, Stores
11. **Manufacturing & Industry** - Textiles, Steel, Pharmaceuticals
12. **Media & Entertainment** - TV, Radio, Production
13. **Beauty & Wellness** - Salons, Spas, Fitness
14. **Sports & Recreation** - Gyms, Sports Clubs, Training
15. **Travel & Tourism** - Travel Agencies, Hotels, Tours

## 🏙️ Supported Cities

**10 Major Pakistani Cities** with area codes:
- Karachi (021)
- Lahore (042)
- Islamabad (051)
- Rawalpindi (051)
- Faisalabad (041)
- Multan (061)
- Hyderabad (022)
- Gujranwala (055)
- Peshawar (091)
- Quetta (081)

## 🔧 Configuration

### **Gemini API Setup**
1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add to `.env` file: `GEMINI_API_KEY=your_key_here`

### **SMTP Configuration**
- **Server**: smtpout.secureserver.net
- **Port**: 465 (SSL)
- **Username**: info@reviu.pk
- **Password**: Your email password

### **Customization**
- Modify `business_collector.py` to add more categories/cities
- Update email templates in `email_generator.py`
- Adjust SMTP settings in `email_sender.py`

## 📈 Monitoring & Analytics

### **Campaign Statistics**
- Total campaigns run
- Total leads generated
- Total emails sent
- Success rate percentage

### **Data Tracking**
- Lead generation sources
- Email delivery status
- Campaign performance
- Historical data analysis

### **Duplicate Prevention**
- Cross-session duplicate checking
- Email and business name validation
- Historical record maintenance

## 🚨 Troubleshooting

### **Common Issues**

1. **Gemini API Errors**
   - Check API key in `.env` file
   - Verify API quota and limits
   - Test connection with "Test Connections" button

2. **SMTP Connection Issues**
   - Verify SMTP credentials
   - Check firewall/network settings
   - Test SMTP connection

3. **Data Loading Problems**
   - Check file permissions for data directory
   - Verify CSV file integrity
   - Use "Clear Session" to reset data

### **Debug Mode**
Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Features

- **Environment Variable Protection** for sensitive data
- **Input Validation** for all user inputs
- **CSRF Protection** in forms
- **Secure SMTP** with SSL/TLS
- **Session Management** with secure keys

## 📁 File Structure

```
├── app.py                 # Main Flask application
├── business_collector.py  # Business lead collection
├── email_generator.py     # AI-powered email generation
├── email_sender.py        # SMTP email delivery
├── data_manager.py        # Data storage and management
├── requirements.txt       # Python dependencies
├── .env                  # Environment configuration
├── templates/
│   └── index.html        # Main web interface
├── static/               # CSS, JS, images
└── data/                 # Generated CSV files
    ├── leads_data.csv
    ├── generated_emails.csv
    ├── campaign_results.csv
    ├── lead_history.csv
    ├── email_history.csv
    ├── sent_emails.csv
    └── campaign_records.json
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software for Reviu.pk. All rights reserved.

## 📞 Support

For technical support or questions:
- **Email**: info@reviu.pk
- **Phone**: 03556924128
- **Website**: https://www.reviu.pk

## 🎉 Acknowledgments

- **Google Gemini AI** for intelligent email generation
- **Flask Framework** for robust web application
- **Bootstrap** for modern UI components
- **Font Awesome** for beautiful icons

---

**Built with ❤️ for Pakistani businesses by the Reviu.pk team**
