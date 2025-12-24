"""
Appointment Functions - Visa Consultant AI Voice Agent

Professional appointment scheduling and visa information system
for Axoraco Visa Consultants.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# SIMULATED DATABASE
# =============================================================================

# Available time slots (in production, connect to real calendar)
BUSINESS_HOURS = {
    "Monday": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
    "Tuesday": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
    "Wednesday": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
    "Thursday": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
    "Friday": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
    "Saturday": ["10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM"],
    "Sunday": []
}

# Visa information database
VISA_INFO = {
    "tourist": {
        "name": "Tourist Visa",
        "consultation_fee": "$50",
        "processing_time": "5-15 business days",
        "common_requirements": [
            "Valid passport (6+ months validity)",
            "Passport-size photographs",
            "Proof of accommodation",
            "Travel itinerary",
            "Bank statements (3 months)",
            "Travel insurance"
        ],
        "description": "Perfect for leisure travel, visiting family, or short vacations abroad."
    },
    "student": {
        "name": "Student Visa",
        "consultation_fee": "$75",
        "processing_time": "2-8 weeks",
        "common_requirements": [
            "Acceptance letter from institution",
            "Proof of financial support",
            "Academic transcripts",
            "Language proficiency test scores",
            "Valid passport",
            "Medical examination"
        ],
        "description": "For pursuing education abroad at universities, colleges, or language schools."
    },
    "work": {
        "name": "Work Visa",
        "consultation_fee": "$100",
        "processing_time": "4-12 weeks",
        "common_requirements": [
            "Job offer letter",
            "Employment contract",
            "Employer sponsorship documents",
            "Professional qualifications",
            "Work experience certificates",
            "Background check"
        ],
        "description": "For employment opportunities in foreign countries."
    },
    "business": {
        "name": "Business Visa",
        "consultation_fee": "$75",
        "processing_time": "1-4 weeks",
        "common_requirements": [
            "Business invitation letter",
            "Company registration documents",
            "Purpose of visit letter",
            "Bank statements",
            "Previous travel history"
        ],
        "description": "For business meetings, conferences, and professional engagements abroad."
    },
    "immigration": {
        "name": "Immigration Consulting",
        "consultation_fee": "$150",
        "processing_time": "Varies by program",
        "common_requirements": [
            "Varies by destination country",
            "Points-based assessment",
            "Language proficiency",
            "Work experience evaluation",
            "Educational credential assessment"
        ],
        "description": "Comprehensive guidance for permanent residency and citizenship applications."
    }
}

# In-memory appointment storage
APPOINTMENTS = {}
CALLBACK_REQUESTS = []

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_confirmation_code() -> str:
    """Generate a unique 6-character confirmation code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def parse_date(date_str: str) -> tuple[str, str]:
    """Parse natural language date to day name and formatted date."""
    today = datetime.now()
    date_lower = date_str.lower().strip()
    
    if date_lower == "today":
        target = today
    elif date_lower == "tomorrow":
        target = today + timedelta(days=1)
    elif date_lower in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        # Find next occurrence of this day
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        target_day = days.index(date_lower)
        current_day = today.weekday()
        days_ahead = (target_day - current_day) % 7
        if days_ahead == 0:
            days_ahead = 7  # Next week if same day
        target = today + timedelta(days=days_ahead)
    else:
        # Try to parse as date
        try:
            for fmt in ["%B %d", "%b %d", "%m/%d", "%d/%m"]:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    target = parsed.replace(year=today.year)
                    if target < today:
                        target = target.replace(year=today.year + 1)
                    break
                except ValueError:
                    continue
            else:
                target = today + timedelta(days=1)  # Default to tomorrow
        except:
            target = today + timedelta(days=1)
    
    day_name = target.strftime("%A")
    formatted_date = target.strftime("%B %d, %Y")
    return day_name, formatted_date


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def get_available_slots(date: str, visa_type: Optional[str] = None) -> str:
    """Get available appointment slots for a specific date."""
    try:
        day_name, formatted_date = parse_date(date)
        
        if day_name not in BUSINESS_HOURS or not BUSINESS_HOURS[day_name]:
            return f"I'm sorry, we're closed on {day_name}s. Our office hours are Monday through Friday 9 AM to 6 PM, and Saturday 10 AM to 2 PM. Would you like to check another day?"
        
        # Simulate some slots being taken
        all_slots = BUSINESS_HOURS[day_name].copy()
        available = [s for s in all_slots if random.random() > 0.3]  # 70% availability
        
        if not available:
            return f"I'm sorry, we're fully booked on {formatted_date}. Would you like to check the next available day?"
        
        slots_text = ", ".join(available[:-1]) + f" and {available[-1]}" if len(available) > 1 else available[0]
        
        response = f"For {formatted_date}, we have appointments available at {slots_text}."
        
        if visa_type and visa_type.lower() in VISA_INFO:
            info = VISA_INFO[visa_type.lower()]
            response += f" A {info['name']} consultation is {info['consultation_fee']}."
        
        response += " Which time works best for you?"
        return response
        
    except Exception as e:
        logger.error(f"Error in get_available_slots: {e}")
        return "I'm having trouble checking availability. Let me connect you with our team. Can I get your phone number for a callback?"


def book_appointment(customer_name: str, phone_number: str, date: str, time: str, visa_type: str) -> str:
    """Book a consultation appointment."""
    try:
        day_name, formatted_date = parse_date(date)
        
        # Validate day is not Sunday
        if day_name == "Sunday":
            return "I'm sorry, we're closed on Sundays. Would you like to book for another day?"
        
        # Generate confirmation
        confirmation_code = generate_confirmation_code()
        
        # Get visa info
        visa_info = VISA_INFO.get(visa_type.lower(), VISA_INFO["tourist"])
        
        # Store appointment
        APPOINTMENTS[confirmation_code] = {
            "customer_name": customer_name,
            "phone_number": phone_number,
            "date": formatted_date,
            "day": day_name,
            "time": time,
            "visa_type": visa_info["name"],
            "fee": visa_info["consultation_fee"],
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Appointment booked: {confirmation_code} for {customer_name}")
        
        return (
            f"Perfect! I've booked your {visa_info['name']} consultation. "
            f"Your appointment is confirmed for {formatted_date} at {time}. "
            f"Your confirmation code is {confirmation_code}. "
            f"The consultation fee is {visa_info['consultation_fee']}, payable at the office. "
            f"We'll send a confirmation to {phone_number}. "
            f"Is there anything else I can help you with?"
        )
        
    except Exception as e:
        logger.error(f"Error in book_appointment: {e}")
        return "I'm having trouble completing the booking. Let me arrange a callback from our team. What's the best number to reach you?"


def get_visa_info(visa_type: str, destination_country: Optional[str] = None) -> str:
    """Get information about a specific visa type."""
    try:
        visa_key = visa_type.lower().strip()
        
        # Match partial visa types
        for key in VISA_INFO:
            if key in visa_key or visa_key in key:
                visa_key = key
                break
        
        if visa_key not in VISA_INFO:
            available = ", ".join([v["name"] for v in VISA_INFO.values()])
            return f"I can help with: {available}. Which type of visa are you interested in?"
        
        info = VISA_INFO[visa_key]
        
        response = f"{info['name']}: {info['description']} "
        response += f"Our consultation fee is {info['consultation_fee']} and typical processing time is {info['processing_time']}. "
        response += f"Common requirements include: {', '.join(info['common_requirements'][:3])} and more. "
        
        if destination_country:
            response += f"Requirements can vary for {destination_country}, so I'd recommend booking a consultation for personalized guidance. "
        
        response += "Would you like to schedule a consultation with one of our experts?"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_visa_info: {e}")
        return "I'd be happy to provide visa information. Could you tell me which type of visa you're interested in? We offer tourist, student, work, business visas and immigration consulting."


def check_appointment(confirmation_code: Optional[str] = None, phone_number: Optional[str] = None) -> str:
    """Check details of an existing appointment."""
    try:
        if confirmation_code and confirmation_code.upper() in APPOINTMENTS:
            apt = APPOINTMENTS[confirmation_code.upper()]
            return (
                f"I found your appointment. "
                f"{apt['customer_name']}, you have a {apt['visa_type']} consultation "
                f"on {apt['date']} at {apt['time']}. "
                f"Status: {apt['status']}. "
                f"Is there anything you'd like to change?"
            )
        
        if phone_number:
            # Search by phone
            for code, apt in APPOINTMENTS.items():
                if apt["phone_number"] == phone_number:
                    return (
                        f"I found an appointment for {apt['customer_name']}. "
                        f"Your {apt['visa_type']} consultation is on {apt['date']} at {apt['time']}. "
                        f"Confirmation code: {code}. "
                        f"Would you like to make any changes?"
                    )
        
        return "I couldn't find an appointment with those details. Could you please provide your confirmation code or the phone number used for booking?"
        
    except Exception as e:
        logger.error(f"Error in check_appointment: {e}")
        return "I'm having trouble looking up your appointment. Can you provide your confirmation code?"


def cancel_appointment(confirmation_code: str, reason: Optional[str] = None) -> str:
    """Cancel an existing appointment."""
    try:
        code = confirmation_code.upper().strip()
        
        if code not in APPOINTMENTS:
            return "I couldn't find an appointment with that confirmation code. Could you please verify the code?"
        
        apt = APPOINTMENTS[code]
        apt["status"] = "cancelled"
        apt["cancellation_reason"] = reason or "Not provided"
        
        logger.info(f"Appointment cancelled: {code}")
        
        return (
            f"I've cancelled your {apt['visa_type']} consultation that was scheduled for {apt['date']} at {apt['time']}. "
            f"If you'd like to reschedule, I'm happy to help you find a new time. "
            f"Is there anything else I can assist with?"
        )
        
    except Exception as e:
        logger.error(f"Error in cancel_appointment: {e}")
        return "I'm having trouble processing the cancellation. Let me connect you with our team."


def request_callback(customer_name: str, phone_number: str, inquiry_type: Optional[str] = None) -> str:
    """Request a callback from a visa consultant."""
    try:
        callback_id = generate_confirmation_code()
        
        CALLBACK_REQUESTS.append({
            "id": callback_id,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "inquiry_type": inquiry_type or "General inquiry",
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        })
        
        logger.info(f"Callback requested: {callback_id} for {customer_name}")
        
        return (
            f"Thank you, {customer_name}. I've submitted a callback request for you. "
            f"One of our visa consultants will call you at {phone_number} within the next 2 business hours. "
            f"Your reference number is {callback_id}. "
            f"Is there anything else I can help you with in the meantime?"
        )
        
    except Exception as e:
        logger.error(f"Error in request_callback: {e}")
        return "I'm having trouble processing your request. Please try calling back or visit our website."


# =============================================================================
# FUNCTION DISPATCHER
# =============================================================================

def execute_function(function_name: str, parameters: dict) -> str:
    """Dispatch function calls from Deepgram to the appropriate handler."""
    functions = {
        "get_available_slots": get_available_slots,
        "book_appointment": book_appointment,
        "get_visa_info": get_visa_info,
        "check_appointment": check_appointment,
        "cancel_appointment": cancel_appointment,
        "request_callback": request_callback,
    }
    
    func = functions.get(function_name)
    if func:
        try:
            logger.info(f"Executing function: {function_name} with params: {parameters}")
            result = func(**parameters)
            logger.info(f"Function result: {result[:100]}...")
            return result
        except TypeError as e:
            logger.error(f"Parameter error in {function_name}: {e}")
            return "I need a bit more information. Could you please provide the missing details?"
        except Exception as e:
            logger.error(f"Error executing {function_name}: {e}")
            return "I'm having a technical issue. Let me arrange a callback from our team."
    
    return "I'm not sure how to help with that. Would you like to speak with a consultant?"


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== Testing Visa Consultant Functions ===\n")
    
    print("1. Getting available slots:")
    print(f"   {get_available_slots('tomorrow', 'student')}\n")
    
    print("2. Getting visa info:")
    print(f"   {get_visa_info('student', 'Canada')}\n")
    
    print("3. Booking appointment:")
    result = book_appointment("John Doe", "+1234567890", "Monday", "10:00 AM", "student")
    print(f"   {result}\n")
    
    print("4. Requesting callback:")
    print(f"   {request_callback('Jane Smith', '+0987654321', 'Immigration to Australia')}\n")
    
    print("=== Tests Complete ===")
