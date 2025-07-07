import React, { useState } from 'react';
import './FAQsPage.css';

const FAQsPage = () => {
  const [openItems, setOpenItems] = useState({});

  const toggleFAQ = (index) => {
    setOpenItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const faqs = [
    {
      question: "What are ProCogia AI agents?",
      answer: "ProCogia AI agents are specialized artificial intelligence solutions designed to automate and enhance specific business processes. Each agent is tailored for particular industries and use cases, providing intelligent automation, analysis, and decision support."
    },
    {
      question: "How do I get started with an AI agent?",
      answer: "Getting started is simple: browse our agents page, book a demo for the agent that interests you, and our team will guide you through a personalized demonstration and integration planning session."
    },
    {
      question: "Can AI agents integrate with my existing systems?",
      answer: "Yes, our AI agents are designed for seamless integration with your existing workflows and systems. We support a wide range of connectors and APIs, and our team can work with you to ensure smooth integration."
    },
    {
      question: "What industries do you serve?",
      answer: "We serve a wide range of industries including Finance, Healthcare, Legal, Manufacturing, Retail, Technology, Energy, Transportation, and Education. Our agents can be customized for specific industry requirements."
    },
    {
      question: "How secure are your AI agents?",
      answer: "Security is our top priority. Our AI agents use enterprise-grade security measures including data encryption, secure API connections, compliance with industry standards, and regular security audits."
    },
    {
      question: "Do you offer custom AI agent development?",
      answer: "Absolutely! While we have pre-built agents for common use cases, we specialize in developing custom AI solutions tailored to your unique business requirements and workflows."
    },
    {
      question: "What kind of support do you provide?",
      answer: "We provide comprehensive support including initial setup assistance, training for your team, ongoing technical support, regular updates, and dedicated account management for enterprise clients."
    },
    {
      question: "How long does implementation take?",
      answer: "Implementation timelines vary depending on the complexity of your requirements. Simple integrations can be completed in a few days, while custom solutions may take several weeks. We'll provide a detailed timeline during your consultation."
    }
  ];

  return (
    <div className="faqs-page">
      <div className="container">
        <div className="page-header">
          <h1>Frequently Asked Questions</h1>
          <p>Find answers to common questions about our AI agents and platform.</p>
        </div>

        <div className="faqs-content">
          <div className="faqs-list">
            {faqs.map((faq, index) => (
              <div key={index} className={`faq-item ${openItems[index] ? 'open' : ''}`}>
                <button 
                  className="faq-question"
                  onClick={() => toggleFAQ(index)}
                >
                  <span>{faq.question}</span>
                  <span className="faq-toggle">{openItems[index] ? '−' : '+'}</span>
                </button>
                {openItems[index] && (
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="faqs-cta">
            <h3>Still have questions?</h3>
            <p>Our team is ready to help you understand how our AI agents can transform your business.</p>
            <div className="cta-buttons">
              <a href="/contact" className="btn-primary">
                Contact Support
              </a>
              <a href="/demos" className="btn-secondary">
                Book a Demo
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQsPage; 