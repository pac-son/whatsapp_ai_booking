import os
import stripe

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

def create_deposit_checkout_session(booking_id: int, service_name: str, deposit_amount: float = 20.0, customer_phone: str = None) -> str:
    """
    Creates a Stripe Checkout Session for a £20 deposit and returns the payment URL.
    If no STRIPE_SECRET_KEY is provided, returns a realistic mock payment link.
    """
    key = os.getenv("STRIPE_SECRET_KEY")
    if not key or key.startswith("your_"):
        # Mock payment URL for sandbox testing before user adds live/test keys
        return f"https://buy.stripe.com/test_deposit?booking_id={booking_id}&amount={int(deposit_amount)}"

    stripe.api_key = key
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"Salon Deposit: {service_name}",
                        "description": f"Securing appointment for booking #{booking_id}",
                    },
                    "unit_amount": int(deposit_amount * 100), # amount in pence
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"https://yourdomain.com/booking-success?session_id={{CHECKOUT_SESSION_ID}}&booking_id={booking_id}",
            cancel_url=f"https://yourdomain.com/booking-cancelled?booking_id={booking_id}",
            metadata={
                "booking_id": str(booking_id),
                "customer_phone": str(customer_phone or "")
            }
        )
        return session.url
    except Exception as e:
        print(f"[STRIPE ERROR] {e}")
        return f"https://buy.stripe.com/test_deposit?booking_id={booking_id}"
