# Salon & Barbershop Business Profiles

BUSINESS_PROFILES = {
    "salon": {
        "business_name": "Aduke Braids & Beauty Lounge",
        "business_type": "Hair Braiding & Beauty Salon",
        "location": "45 Rye Lane, Peckham, London SE15 5ER",
        "deposit_amount": 20.0,
        "hours": "Tue - Sat: 9:00 AM - 7:00 PM | Sun: 11:00 AM - 5:00 PM | Mon: Closed",
        "services": [
            {"name": "Medium Knotless Braids", "price": 120.0, "duration": "4 hrs"},
            {"name": "Small Knotless Braids", "price": 160.0, "duration": "5-6 hrs"},
            {"name": "Traditional Box Braids", "price": 100.0, "duration": "4 hrs"},
            {"name": "Stitch Cornrows", "price": 50.0, "duration": "1.5 hrs"},
            {"name": "Goddess Boho Braids", "price": 150.0, "duration": "5 hrs"}
        ]
    },
    "barbershop": {
        "business_name": "Krowns & Fades Afro Barbershop",
        "business_type": "Afro Barbershop & Grooming",
        "location": "112 Walworth Road, Elephant & Castle, London SE17 1JL",
        "deposit_amount": 10.0,
        "hours": "Mon - Sat: 9:00 AM - 8:00 PM | Sun: 10:00 AM - 6:00 PM",
        "services": [
            {"name": "Skin Fade & Line Up", "price": 30.0, "duration": "45 mins"},
            {"name": "Traditional Haircut & Shape Up", "price": 25.0, "duration": "30 mins"},
            {"name": "Beard Sculpt, Trim & Hot Towel Treatment", "price": 20.0, "duration": "30 mins"},
            {"name": "The VIP Full Service (Cut, Beard, Wash & Facial)", "price": 55.0, "duration": "1 hr 15 mins"},
            {"name": "Kids / Student Fade", "price": 20.0, "duration": "30 mins"}
        ]
    }
}

ACTIVE_VERTICAL = "barbershop" # Can be toggled between "salon" and "barbershop"

def get_active_profile():
    return BUSINESS_PROFILES.get(ACTIVE_VERTICAL, BUSINESS_PROFILES["salon"])
