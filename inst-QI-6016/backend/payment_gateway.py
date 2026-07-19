from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os

class PaymentGateway(ABC):
    """Abstract base class for payment gateway integrations."""

    @abstractmethod
    def create_payment_intent(
        self,
        amount_cents: int,
        currency_code: str,
        description: str,
        metadata: Dict[str, Any],
        return_url: str,
    ) -> Dict[str, Any]:
        """
        Creates a payment intent with the payment gateway.

        Args:
            amount_cents: The amount to charge in cents.
            currency_code: The currency code (e.g., "USD").
            description: A description of the payment.
            metadata: Arbitrary key-value pairs to store with the payment.
            return_url: The URL to redirect the user to after payment completion.

        Returns:
            A dictionary containing payment initiation details (e.g., client_secret, redirect_url).
        """
        pass

    @abstractmethod
    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Handles an incoming webhook from the payment gateway.

        Args:
            payload: The raw payload from the webhook.
            signature: The signature header for verification.

        Returns:
            A dictionary containing the processed event data.
        """
        pass

class DummyPaymentGateway(PaymentGateway):
    """
    A dummy payment gateway for development and testing.
    It simulates successful payments without actual financial transactions.
    """
    def create_payment_intent(
        self,
        amount_cents: int,
        currency_code: str,
        description: str,
        metadata: Dict[str, Any],
        return_url: str,
    ) -> Dict[str, Any]:
        print(f"DummyPaymentGateway: Creating payment intent for {amount_cents} {currency_code}")
        # Simulate a successful payment intent creation that requires client-side confirmation
        return {
            "client_secret": f"dummy_client_secret_{amount_cents}_{metadata['product_id']}_{metadata['tenant_id']}_{metadata['user_id']}_{metadata['questions_quota']}_{metadata['audience_type']}_{metadata['amount_cents']}_{metadata['currency_code']}",
            "payment_intent_id": "dummy_pi_" + str(amount_cents),
            "status": "requires_action", # Simulate needing user action
            "metadata": metadata # Pass metadata directly for client-side use
        }

    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        print(f"DummyPaymentGateway: Handling webhook with payload: {payload}")
        # In a real scenario, verify signature and parse event
        # For dummy, we'll just assume it's a success event
        return {
            "id": payload.get("id", "dummy_evt_" + str(hash(str(payload)))),
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": payload.get("payment_intent_id", "dummy_pi_webhook"),
                    "amount": payload.get("data", {}).get("object", {}).get("amount"), # Correctly get amount
                    "currency": payload.get("data", {}).get("object", {}).get("currency"), # Correctly get currency
                    "metadata": payload.get("data", {}).get("object", {}).get("metadata", {}),
                    "status": "succeeded",
                }
            }
        }

# Global instance of the payment gateway (can be swapped for a real one)
_payment_gateway_instance: Optional[PaymentGateway] = None

def get_payment_gateway() -> PaymentGateway:
    global _payment_gateway_instance
    if _payment_gateway_instance is None:
        if os.getenv("USE_DUMMY_PAYMENT_GATEWAY", "true").lower() in ("false", "0"):
            stripe_api_key = os.getenv("STRIPE_API_KEY")
            if not stripe_api_key:
                raise ValueError("STRIPE_API_KEY environment variable not set for StripePaymentGateway")
            _payment_gateway_instance = StripePaymentGateway(api_key=stripe_api_key)
            print("Using StripePaymentGateway")
        else:
            _payment_gateway_instance = DummyPaymentGateway()
            print("Using DummyPaymentGateway")
    return _payment_gateway_instance
