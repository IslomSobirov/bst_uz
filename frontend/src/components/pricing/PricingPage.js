import React from 'react';
import { Pricing } from './Pricing';

const demoPlans = [
  {
    name: "FREE",
    price: "0",
    yearlyPrice: "0",
    period: "per month",
    features: [
      "Browse all creators",
      "View free posts",
      "Basic profile",
      "Community access",
      "Email notifications",
    ],
    description: "Perfect for exploring the platform",
    buttonText: "Get Started",
    href: "#",
    isPopular: false,
  },
  {
    name: "CREATOR",
    price: "15",
    yearlyPrice: "12",
    period: "per month",
    features: [
      "Everything in Free",
      "Create unlimited posts",
      "Subscription tiers",
      "Analytics dashboard",
      "Priority support",
      "Custom branding",
      "Exclusive content tools",
    ],
    description: "Ideal for content creators and artists",
    buttonText: "Become a Creator",
    href: "#",
    isPopular: true,
  },
  {
    name: "PREMIUM",
    price: "29",
    yearlyPrice: "23",
    period: "per month",
    features: [
      "Everything in Creator",
      "Advanced analytics",
      "Custom domain",
      "API access",
      "White-label options",
      "Dedicated account manager",
      "Custom integrations",
      "Early access to features",
    ],
    description: "For professional creators and businesses",
    buttonText: "Go Premium",
    href: "#",
    isPopular: false,
  },
];

function PricingPage({ onBack }) {
  return (
    <div className="min-h-screen bg-background">
      {onBack && (
        <div className="container py-4">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="m15 18-6-6 6-6" />
            </svg>
            Back
          </button>
        </div>
      )}
      <Pricing
        plans={demoPlans}
        title="Choose Your Plan"
        description="Join thousands of creators building their community on Boosty\nFlexible plans designed to grow with you"
      />
    </div>
  );
}

export default PricingPage;
