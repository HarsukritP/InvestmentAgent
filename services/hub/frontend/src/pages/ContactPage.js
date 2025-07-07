import React from 'react';
import './ContactPage.css';

const ContactPage = () => {
  return (
    <div className="contact-page">
      <div className="container">
        <div className="page-header">
          <h1>Contact Us</h1>
          <p>Get in touch with our team to discuss your AI needs and explore custom solutions.</p>
        </div>

        <div className="contact-content">
          <div className="contact-form-section">
            <h2>Send us a message</h2>
            <form className="contact-form">
              <div className="form-row">
                <div className="form-group">
                  <label>First Name *</label>
                  <input type="text" required />
                </div>
                <div className="form-group">
                  <label>Last Name *</label>
                  <input type="text" required />
                </div>
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input type="email" required />
              </div>
              <div className="form-group">
                <label>Company</label>
                <input type="text" />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input type="tel" />
              </div>
              <div className="form-group">
                <label>Subject</label>
                <select>
                  <option>General Inquiry</option>
                  <option>Demo Request</option>
                  <option>Custom Solution</option>
                  <option>Technical Support</option>
                  <option>Partnership</option>
                </select>
              </div>
              <div className="form-group">
                <label>Message *</label>
                <textarea rows="5" required placeholder="Tell us about your project or questions..."></textarea>
              </div>
              <button type="submit" className="btn-primary">
                Send Message
              </button>
            </form>
          </div>

          <div className="contact-info-section">
            <h3>Get in Touch</h3>
            <div className="contact-methods">
              <div className="contact-method">
                <h4>📧 Email</h4>
                <p>hello@procogia.com</p>
                <p>support@procogia.com</p>
              </div>
              <div className="contact-method">
                <h4>📞 Phone</h4>
                <p>+1 (555) 123-4567</p>
              </div>
              <div className="contact-method">
                <h4>🏢 Office</h4>
                <p>123 AI Innovation Drive<br />
                San Francisco, CA 94105<br />
                United States</p>
              </div>
            </div>

            <div className="business-hours">
              <h4>Business Hours</h4>
              <p>Monday - Friday: 9:00 AM - 6:00 PM PST<br />
              Saturday: 10:00 AM - 2:00 PM PST<br />
              Sunday: Closed</p>
            </div>

            <div className="response-time">
              <h4>Response Time</h4>
              <p>We typically respond to inquiries within 24 hours during business days.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage; 