"""
Voice Sample Content for Chat&Talk GPT Voice Assistants
=========================================================

This module contains ready-to-use text content for voice synthesis
using ElevenLabs API. It includes samples for two voice assistants:

1. AABINASH (Male) - Confident, Professional, Natural Human-like Tone
   - English samples
   - Nepali samples  
   - Hindi samples

2. AANKANSHA (Female) - Warm, Professional, Natural Human-like Tone
   - Nepali samples

Each assistant has samples covering:
- Greetings
- Weather Updates
- Reminders
- Directions
- General Assistance

Phonetic guides included for non-English words.
"""

# ==============================================================================
# AABINASH (MALE) - CONFIDENT, PROFESSIONAL VOICE
# Voice ID: pNInz6obpgDQGcFmaJgB (Adam - ElevenLabs)
# ==============================================================================

AABINASH_ENGLISH = {
    "greetings": [
        {
            "id": "en_ab_greet_1",
            "text": "Good morning! I am Aabinash, your personal voice assistant. How may I help you today?",
            "phonetics": "N/A - English",
            "scenario": "Morning greeting"
        },
        {
            "id": "en_ab_greet_2",
            "text": "Hello! Welcome back. I'm here to assist you with any task you need. What can I do for you?",
            "phonetics": "N/A - English",
            "scenario": "General greeting"
        },
        {
            "id": "en_ab_greet_3",
            "text": "Good afternoon! I hope you're having a productive day. How can I be of service?",
            "phonetics": "N/A - English",
            "scenario": "Afternoon greeting"
        },
        {
            "id": "en_ab_greet_4",
            "text": "Good evening! I'm Aabinash, ready to help you wrap up your day. What would you like to accomplish?",
            "phonetics": "N/A - English",
            "scenario": "Evening greeting"
        },
        {
            "id": "en_ab_greet_5",
            "text": "Hey there! Great to hear from you again. Let's get things done together today.",
            "phonetics": "N/A - English",
            "scenario": "Casual greeting"
        }
    ],
    "weather": [
        {
            "id": "en_ab_weather_1",
            "text": "The current temperature is 22 degrees Celsius with partly cloudy skies. It feels quite pleasant outside.",
            "phonetics": "N/A - English",
            "scenario": "Weather update - pleasant"
        },
        {
            "id": "en_ab_weather_2",
            "text": "Today's forecast shows heavy rainfall expected in the afternoon. Don't forget your umbrella!",
            "phonetics": "N/A - English",
            "scenario": "Weather update - rainy"
        },
        {
            "id": "en_ab_weather_3",
            "text": "It's currently sunny with a temperature of 28 degrees. Perfect weather for outdoor activities.",
            "phonetics": "N/A - English",
            "scenario": "Weather update - sunny"
        },
        {
            "id": "en_ab_weather_4",
            "text": "Expect foggy conditions tomorrow morning with visibility around 500 meters. Drive safely if you're traveling.",
            "phonetics": "N/A - English",
            "scenario": "Weather update - foggy"
        },
        {
            "id": "en_ab_weather_5",
            "text": "The temperature will drop to 15 degrees tonight. You might want to grab a light jacket.",
            "phonetics": "N/A - English",
            "scenario": "Weather update - cold"
        }
    ],
    "reminders": [
        {
            "id": "en_ab_remind_1",
            "text": "Reminder: You have a meeting with the team in 30 minutes. Shall I send a notification to prepare?",
            "phonetics": "N/A - English",
            "scenario": "Meeting reminder"
        },
        {
            "id": "en_ab_remind_2",
            "text": "Don't forget to pick up groceries on your way home. The list includes vegetables, fruits, and milk.",
            "phonetics": "N/A - English",
            "scenario": "Shopping reminder"
        },
        {
            "id": "en_ab_remind_3",
            "text": "Your prescription is due for refill tomorrow. Would you like me to remind you again in the morning?",
            "phonetics": "N/A - English",
            "scenario": "Health reminder"
        },
        {
            "id": "en_ab_remind_4",
            "text": "Birthday reminder: Your friend Sarah's birthday is tomorrow. Don't forget to wish her!",
            "phonetics": "N/A - English",
            "scenario": "Birthday reminder"
        },
        {
            "id": "en_ab_remind_5",
            "text": "Payment due: Your electricity bill is due in 3 days. The amount is 2500 rupees.",
            "phonetics": "N/A - English",
            "scenario": "Bill reminder"
        }
    ],
    "directions": [
        {
            "id": "en_ab_direct_1",
            "text": "To reach the nearest hospital, turn right at the main intersection, then go straight for about 500 meters. It will be on your left.",
            "phonetics": "N/A - English",
            "scenario": "Directions to hospital"
        },
        {
            "id": "en_ab_direct_2",
            "text": "The bus station is about 2 kilometers away. Head north on this road, and you'll see it on the right side near the clock tower.",
            "phonetics": "N/A - English",
            "scenario": "Directions to bus station"
        },
        {
            "id": "en_ab_direct_3",
            "text": "For the shopping mall, take the highway eastbound. Exit at the third toll gate, and follow the signs to City Center Mall.",
            "phonetics": "N/A - English",
            "scenario": "Directions to mall"
        },
        {
            "id": "en_ab_direct_4",
            "text": "The nearest ATM is just around the corner, about 100 meters down this street on the right side.",
            "phonetics": "N/A - English",
            "scenario": "Directions to ATM"
        },
        {
            "id": "en_ab_direct_5",
            "text": "To get to the airport, I recommend taking the expressway. It's approximately 25 minutes depending on traffic.",
            "phonetics": "N/A - English",
            "scenario": "Directions to airport"
        }
    ],
    "general": [
        {
            "id": "en_ab_gen_1",
            "text": "I've added that task to your list. Is there anything else you'd like me to help with?",
            "phonetics": "N/A - English",
            "scenario": "Task completion"
        },
        {
            "id": "en_ab_gen_2",
            "text": "I've searched for the best restaurants nearby. Would you like me to read out the top three options?",
            "phonetics": "N/A - English",
            "scenario": "Restaurant search"
        },
        {
            "id": "en_ab_gen_3",
            "text": "Your schedule for tomorrow looks busy. You have 5 meetings starting from 9 AM. Should I help you prepare?",
            "phonetics": "N/A - English",
            "scenario": "Schedule review"
        },
        {
            "id": "en_ab_gen_4",
            "text": "I've sent the email to your colleague. Is there anything else you'd like me to help you with?",
            "phonetics": "N/A - English",
            "scenario": "Email assistance"
        },
        {
            "id": "en_ab_gen_5",
            "text": "Would you like me to play some music? I can play your favorite playlist or suggest something new.",
            "phonetics": "N/A - English",
            "scenario": "Entertainment offer"
        }
    ]
}

AABINASH_NEPALI = {
    "greetings": [
        {
            "id": "ne_ab_greet_1",
            "text": "शुभ प्रभात! म Aabinash हुँ, तपाईंको व्यक्तिगत भ्वाइस सहायक। आज म तपाईंलाई कसरी मद्दत गर्न सक्छु?",
            "phonetics": "Shubha prabhat! Ma Aabinash hum, tapaiko byatika bhvais sahayak. Aaj ma tapaikai kasari madad garna sakhchu?",
            "scenario": "Morning greeting"
        },
        {
            "id": "ne_ab_greet_2",
            "text": "नमस्ते! स्वागत छ। म तपाईंको कुनै पनि कार्यमा सहायता गर्न तयार छु। के गर्न चाहनुहुन्छ?",
            "phonetics": "Namaste! Swagat chha. Ma tapaiko kunai pani karyama sahayata garna tayair chhu. Ke garna chahānuhunchha?",
            "scenario": "General greeting"
        },
        {
            "id": "ne_ab_greet_3",
            "text": "शुभ दिउँसो! आजको दिन उत्पादक भएको आशा राख्छु। कसरी सहायता गर्न सक्छु?",
            "phonetics": "Shubha diuso! Aajako dina utpadak bhayeko ashā rakhchhu. Kasari sahayata garna sakhchu?",
            "scenario": "Afternoon greeting"
        },
        {
            "id": "ne_ab_greet_4",
            "text": "शुभ साँझ! म Aabinash तपाईंको दिन समाप्त गर्न मद्दत गर्न तयार छु। के गर्न चाहनुहुन्छ?",
            "phonetics": "Shubha sanjha! Ma Aabinash tapaiko dina samapt garna madad garna tayair chhu. Ke garna chahānuhunchha?",
            "scenario": "Evening greeting"
        },
        {
            "id": "ne_ab_greet_5",
            "text": "नमस्ते! तपाईंबाट फेरि सुन्यौ राम्रो भयो। आज हामी मिलेर काम गरौं।",
            "phonetics": "Namaste! tapaibaat feri sunyau ramro bhayo. Aaj hami milera kam garau.",
            "scenario": "Casual greeting"
        }
    ],
    "weather": [
        {
            "id": "ne_ab_weather_1",
            "text": "हालको तापक्रम 22 डिग्री सेल्सियस र आंशिक रूपमा बादल छ। बाहिर धेरै राम्रो छ।",
            "phonetics": "Halko tapakraam 22 degree celsius ra ansik rupama badal chha. Bahir dherai ramro chha.",
            "scenario": "Weather update - pleasant"
        },
        {
            "id": "ne_ab_weather_2",
            "text": "आजको पूर्वानुमानअनुसार दिउँसोमा भारी वर्षा हुने अपेक्षा छ। आफ्नो छाता लिन नबिर्सनु!",
            "phonetics": "Aajko purvanuman anusara diunsoma bhari varsha hune apeksha chha. Apno chhata lina birisnu!",
            "scenario": "Weather update - rainy"
        },
        {
            "id": "ne_ab_weather_3",
            "text": "हाल घाम लागिरहेको छ र तापक्रम 28 डिग्री सेल्सियस छ। बाहिरका गतिविधिहरूको लागि उत्तम मौसम।",
            "phonetics": "Hala gham lagirihako chha ra tapakraam 28 degree celsius chha. Bahirka gatividhiharu ko lagi uttam mausam.",
            "scenario": "Weather update - sunny"
        },
        {
            "id": "ne_ab_weather_4",
            "text": "भोलि बिहान हिम्मे हुने अपेक्षा छ, दृश्यता करिब 500 मिटर छ। यात्रा गर्दा सावधान रहनुहोस्।",
            "phonetics": "Boli bihana himme hune apeksha chha, drishyta karib 500 meter chha. Yatra garda savdhan rahunuhos.",
            "scenario": "Weather update - foggy"
        },
        {
            "id": "ne_ab_weather_5",
            "text": "आज राति तापक्रम 15 डिग्री सेल्सियसमा झर्नेछ। तपाईंलाई हल्का ज्याकट चाहिन्छ।",
            "phonetics": "Aaj rati tapakraam 15 degree celsius ma jharnachha. Tapaikai halka jacket chahinchha.",
            "scenario": "Weather update - cold"
        }
    ],
    "reminders": [
        {
            "id": "ne_ab_remind_1",
            "text": "अनुस्मारक: तपाईंसँग 30 मिनटमा टिमसँग बैठक छ। तयारीका लागि सूचना पठाउने?",
            "phonetics": "Anusmarak: Tapaaisanga 30 minutama timsanga baithak chha. Tayari ko lagi suchana pathaune?",
            "scenario": "Meeting reminder"
        },
        {
            "id": "ne_ab_remind_2",
            "text": "घर जाने बाटोमा किराना किन्न नबिर्सनु। सूचीमा तरकारी, फलफूल र दूध छ।",
            "phonetics": "Ghar jane batoma kirana kinna birisnu. Suchima tarakari, phalphul ra dudh chha.",
            "scenario": "Shopping reminder"
        },
        {
            "id": "ne_ab_remind_3",
            "text": "तपाईंको prescription भोलि refill गर्ने मिति छ। म बिहान फेरि अनुस्मारक दिने?",
            "phonetics": "Tapaiko prescription boli refill garne miti chha. Ma bihana feri anusmarak dine?",
            "scenario": "Health reminder"
        },
        {
            "id": "ne_ab_remind_4",
            "text": "जन्मदिन अनुस्मारक: तपाईंकी साथी Sarah को भोलि जन्मदिन हो। शुभकामना दिन नबिर्सनु!",
            "phonetics": "Janmadina anusmarak: Tapaiki sathi Sarah ko boli janmadina ho. Shubhakamana dina birisnu!",
            "scenario": "Birthday reminder"
        },
        {
            "id": "ne_ab_remind_5",
            "text": "भुक्तानी देय: तपाईंको बिजुली बिल 3 दिनमा तिर्नुपर्छ। रकम 2500 रुपैयाँ छ।",
            "phonetics": "Bhuktani dey: Tapaiko bijuli bil 3 dinama tirnuparchha. Rakam 2500 rupaiya chha.",
            "scenario": "Bill reminder"
        }
    ],
    "directions": [
        {
            "id": "ne_ab_direct_1",
            "text": "नजिकैको अस्पताल पुग्न मुख्य चोकमा दायाँ मोड्नुहोस्, त्यसपछि करिब 500 मिटर सोझै जानुहोस्। यो तपाईंको बायाँमा हुनेछ।",
            "phonetics": "Najikko aspatal pugna mukhya chokma dayan modnuhos, tyasapachi karib 500 meter sojha januhos. Yo tapaiko bayanma hunechha.",
            "scenario": "Directions to hospital"
        },
        {
            "id": "ne_ab_direct_2",
            "text": "बस स्टेशन करिब 2 किलोमिटर टाढा छ। यो सडकमा उत्तरतर्फ जानुहोस्, घडी टावरको नजिकै दायाँपट्टि देख्नुहुनेछ।",
            "phonetics": "Bas station karib 2 kilometar tadha chha. Yo sadakma uttartatrab januhos, ghadi tower ko najik dayanpatti dekhnu hunchhe.",
            "scenario": "Directions to bus station"
        },
        {
            "id": "ne_ab_direct_3",
            "text": "किनमेल मल जानको लागि पूर्वी हाइवे लिनुहोस्। तेस्रो टोल गेटबाट निस्कनुहोस् र City Center Mall को संकेत पछ्याउनुहोस्।",
            "phonetics": "Kinamal mala janko lagi purbi highway linuhos. Tesro tol gate bata niskunuhos ra City Center Mall ko sanket pachyauhnuhos.",
            "scenario": "Directions to mall"
        },
        {
            "id": "ne_ab_direct_4",
            "text": "नजिकैको ATM यहीँ कोनामा करिब 100 मिटर तल यो सडकको दायाँपट्टि छ।",
            "phonetics": "Najikko ATM yihin konama karib 100 meter tal yo sadakko dayanpatti chha.",
            "scenario": "Directions to ATM"
        },
        {
            "id": "ne_ab_direct_5",
            "text": "हवाई अड्डा जानको लागि म expressway लिने सुझाव दिन्छु। ट्रैफिकको आधारमा करिब 25 मिनट लाग्छ।",
            "phonetics": "Hawai adda janko lagi ma expressway line sujhab dinchhu. Traffic ko adharama karib 25 minut lagchha.",
            "scenario": "Directions to airport"
        }
    ],
    "general": [
        {
            "id": "ne_ab_gen_1",
            "text": "मैले तपाईंको कार्यसूचीमा त्यो कार्य थपें। अरू केही मद्दत चाहनुहुन्छ?",
            "phonetics": "Maile tapaiko karyasuchima tyo kary thapay. Aaru kehi madad chahānuhunchha?",
            "scenario": "Task completion"
        },
        {
            "id": "ne_ab_gen_2",
            "text": "मैले नजिकैका उत्तम रेस्टुरेन्टहरू खोजें। म तपाईंलाई शीर्ष तीन विकल्प पढेर सुनाउने?",
            "phonetics": "Maile najikka uttam restaurant haru khojay. Ma tapaikai shirsha tin vikalp padher sunau?",
            "scenario": "Restaurant search"
        },
        {
            "id": "ne_ab_gen_3",
            "text": "तपाईंको भोलिको तालिका व्यस्त देखिन्छ। तपाईंसँग बिहान 9 बजेदेखि 5 वटा बैठकहरू छन्। तयारीमा मद्दत चाहनुहुन्छ?",
            "phonetics": "Tapaiko boliko talika vyast dekhincha. Tapaaisanga bihana 9 bajedekhi 5 vata baithak haru chhan. Tayari ma madad chahānuhunchha?",
            "scenario": "Schedule review"
        },
        {
            "id": "ne_ab_gen_4",
            "text": "मैले तपाईंको सहायकलाई इमेल पठाएँ। अरू केही मद्दत चाहनुहुन्छ?",
            "phonetics": "Maile tapaiko sahayatlai email pathayen. Aaru kehi madad chahānuhunchha?",
            "scenario": "Email assistance"
        },
        {
            "id": "ne_ab_gen_5",
            "text": "के तपाईंलाई केही संगीत बजाउने मन छ? म तपाईंको मनपर्ने playlist बजाउन सक्छु वा नयाँ केही सुझाउन सक्छु।",
            "phonetics": "Ke tapaikai kehi sangeet bajaune man chha? Ma tapaiko manparne playlist bajawn sakhchu va naya kehi sujhaun sakhchu.",
            "scenario": "Entertainment offer"
        }
    ]
}

AABINASH_HINDI = {
    "greetings": [
        {
            "id": "hi_ab_greet_1",
            "text": "सुप्रभात! मैं Aabinash हूं, आपका व्यक्तिगत वॉइस असिस्टेंट। आज मैं आपकी कैसे मदद कर सकता हूं?",
            "phonetics": "Suprabhat! Main Aabinash hoon, aapka vyaktigat voice assistant. Aaj main aapki kaise madad kar sakta hoon?",
            "scenario": "Morning greeting"
        },
        {
            "id": "hi_ab_greet_2",
            "text": "नमस्ते! वापस स्वागत है। मैं आपके किसी भी कार्य में सहायता के लिए तैयार हूं। आप मुझसे क्या चाहते हैं?",
            "phonetics": "Namaste! Vapas swagat hai. Main aapke kisi bhi kary mein sahayata ke liye tayair hoon. Aap mujhse kya chahate hain?",
            "scenario": "General greeting"
        },
        {
            "id": "hi_ab_greet_3",
            "text": "शुभ दोपहर! उम्मीद है आपका दिन उत्पादक बीत रहा है। मैं कैसे सहायता कर सकता हूं?",
            "phonetics": "Shubha dopahar! Umeed hai aapka din utpadak beeta raha hai. Main kaise sahayata kar sakta hoon?",
            "scenario": "Afternoon greeting"
        },
        {
            "id": "hi_ab_greet_4",
            "text": "शुभ संध्या! मैं Aabinash आपके दिन को समाप्त करने में मदद के लिए तैयार हूं। आप क्या पूरा करना चाहेंगे?",
            "phonetics": "Shubha sandhya! Main Aabinash aapke din ko samapt karne mein madad ke liye tayair hoon. Aap kya pura karna chahenge?",
            "scenario": "Evening greeting"
        },
        {
            "id": "hi_ab_greet_5",
            "text": "नमस्ते! आपसे फिर से बात करके अच्छा लगा। आज मिलकर काम करते हैं।",
            "phonetics": "Namaste! Aapse phir se baat karake achcha laga. Aaj milkar kaam karte hain.",
            "scenario": "Casual greeting"
        }
    ],
    "weather": [
        {
            "id": "hi_ab_weather_1",
            "text": "वर्तमान तापमान 22 डिग्री सेल्सियस है आंशिक रूप से बादल है। बाहर khushkpasand weather है।",
            "phonetics": "Vartman tapaman 22 degree celsius hai, ansik rup se badal hai. Bahar bahut achcha mausam hai.",
            "scenario": "Weather update - pleasant"
        },
        {
            "id": "hi_ab_weather_2",
            "text": "आज के पूर्वानुमान के अनुसार दोपहर में भारी बारिश होने की उम्मीद है। अपना छाता लेना न भूलें!",
            "phonetics": "Aaj ke purvanuman ke anusara dopahar mein bhari barish hone ki ummeed hai. Apna chhata lena na bhoolen!",
            "scenario": "Weather update - rainy"
        },
        {
            "id": "hi_ab_weather_3",
            "text": "अभी धूप है और तापमान 28 डिग्री सेल्सियस है। बाहरी गतिविधियों के लिए बढ़िया मौसम।",
            "phonetics": "Abhi dhoop hai aur tapaman 28 degree celsius hai. Bahri gatividhiyon ke liye badhiya mausam.",
            "scenario": "Weather update - sunny"
        },
        {
            "id": "hi_ab_weather_4",
            "text": "कल सुबह कोहरा होने की उम्मीद है, दृश्यता लगभग 500 मीटर है। यात्रा करते समय सावधान रहें।",
            "phonetics": "Kal subah kohra hone ki ummeed hai, drishyta lagbhag 500 meter hai. Yatra karte samay savdhan rahein.",
            "scenario": "Weather update - foggy"
        },
        {
            "id": "hi_ab_weather_5",
            "text": "आज रात तापमान 15 डिग्री सेल्सियस तक गिर जाएगा। आपको हल्की जैकेट की जरूरत पड़ सकती है।",
            "phonetics": "Aaj rat tapaman 15 degree celsius tak gir jayega. Aapko halki jacket ki zarurat pad sakti hai.",
            "scenario": "Weather update - cold"
        }
    ],
    "reminders": [
        {
            "id": "hi_ab_remind_1",
            "text": "रिमाइंडर: आपकी टीम के साथ 30 मिनट में मीटिंग है। क्या मैं तैयारी के लिए नोटिफिकेशन भेज दूं?",
            "phonetics": "Reminder: Aapki team ke sath 30 minut mein meeting hai. Kya main tayari ke liye notification bhej doon?",
            "scenario": "Meeting reminder"
        },
        {
            "id": "hi_ab_remind_2",
            "text": "घर जाते समय किराना लेना न भूलें। सूची में सब्जियां, फल और दूध शामिल हैं।",
            "phonetics": "Ghar jate samay kirana lena na bhoolen. Suchi mein sabziyan, fal aur doodh shamil hain.",
            "scenario": "Shopping reminder"
        },
        {
            "id": "hi_ab_remind_3",
            "text": "आपका प्रिस्क्रिप्शन कल रिफिल की तारीख है। क्या मैं सुबह फिर से रिमाइंडर दूं?",
            "phonetics": "Aapka prescription kal refill ki taareekh hai. Kya main subah phir se reminder doon?",
            "scenario": "Health reminder"
        },
        {
            "id": "hi_ab_remind_4",
            "text": "जन्मदिन रिमाइंडर: आपकी दोस्त Sarah का कल जन्मदिन है। उन्हें शुभकामना देना न भूलें!",
            "phonetics": "Janmdin reminder: Aapki dost Sarah ka kal janmdin hai. Unhe shubhakamana dena na bhoolen!",
            "scenario": "Birthday reminder"
        },
        {
            "id": "hi_ab_remind_5",
            "text": "भुगतान देय: आपका बिजली बिल 3 दिन में देय है। राशि 2500 रुपये है।",
            "phonetics": "Bhugatan dey: Aapka bijli bil 3 din mein dey hai. Rashi 2500 rupee hai.",
            "scenario": "Bill reminder"
        }
    ],
    "directions": [
        {
            "id": "hi_ab_direct_1",
            "text": "निकटतम अस्पताल पहुंचने के लिए मुख्य चौराहे पर दाएं मुड़ें, फिर लगभग 500 मीटर सीधे जाएं। यह आपके बाएं पर होगा।",
            "phonetics": "Niktatam aspatal pahunchne ke liye mukhya chowrahe par dayen muden, phir lagbhag 500 meter sidhe jayen. Yeh aapke bayen par hoga.",
            "scenario": "Directions to hospital"
        },
        {
            "id": "hi_ab_direct_2",
            "text": "बस स्टेशन लगभग 2 किलोमीटर दूर है। इस सड़क पर उत्तर की ओर जाएं, घड़ी टावर के पास दाएं ओर दिखाई देगा।",
            "phonetics": "Bas station lagbhag 2 kilometar door hai. Is sadak par uttar ki or jayen, ghadi tower ke pas dayen or dikhai dega.",
            "scenario": "Directions to bus station"
        },
        {
            "id": "hi_ab_direct_3",
            "text": "शॉपिंग मॉल जाने के लिए पूर्वी हाइवे लें। तीसरे टोल गेट से बाहर निकलें और City Center Mall के संकेतों का पालन करें।",
            "phonetics": "Shopping mall jane ke liye purbi highway len. Tisre tol gate se bahar niklen aur City Center Mall ke sanketon ka palan karein.",
            "scenario": "Directions to mall"
        },
        {
            "id": "hi_ab_direct_4",
            "text": "निकटतम ATM इसी कोने में लगभग 100 मीटर नीचे इस सड़क के दाएं ओर है।",
            "phonetics": "Niktatam ATM isi kone mein lagbhag 100 meter niche is sadak ke dayen or hai.",
            "scenario": "Directions to ATM"
        },
        {
            "id": "hi_ab_direct_5",
            "text": "एयरपोर्ट जाने के लिए मैं एक्सप्रेसवे लेने की सलाह देता हूं। ट्रैफिक के आधार पर यह लगभग 25 मिनट लेगा।",
            "phonetics": "Airport jane ke liye main expressway lene ki salah deta hoon. Traffic ke adhar par yeh lagbhag 25 minut lega.",
            "scenario": "Directions to airport"
        }
    ],
    "general": [
        {
            "id": "hi_ab_gen_1",
            "text": "मैंने वह कार्य आपकी सूची में जोड़ दिया है। क्या आपको कुछ और मदद चाहिए?",
            "phonetics": "Mainne woh kary aapki suchi mein jod diya hai. Kya aapko kuch aur madad chahiye?",
            "scenario": "Task completion"
        },
        {
            "id": "hi_ab_gen_2",
            "text": "मैंने आसपास के सर्वश्रेष्ठ रेस्तरां खोज लिए हैं। क्या मैं आपको शीर्ष तीन विकल्प सुनाऊं?",
            "phonetics": "Mainne aaspass ke sarshreshth restaurant khoj liye hain. Kya main aapko shirsha tin vikalp sunau?",
            "scenario": "Restaurant search"
        },
        {
            "id": "hi_ab_gen_3",
            "text": "आपकी कल की शेड्यूल व्यस्त दिख रही है। सुबह 9 बजे से 5 मीटिंग हैं। क्या मैं तैयारी में मदद करूं?",
            "phonetics": "Aapki kal ki schedule vyast dikh rahi hai. Subah 9 baje se 5 meeting hain. Kya main tayari mein madad karoon?",
            "scenario": "Schedule review"
        },
        {
            "id": "hi_ab_gen_4",
            "text": "मैंने आपके सहयोगी को ईमेल भेज दिया है। क्या आपको कुछ और मदद चाहिए?",
            "phonetics": "Mainne aapke sahayogi ko email bhej diya hai. Kya aapko kuch aur madad chahiye?",
            "scenario": "Email assistance"
        },
        {
            "id": "hi_ab_gen_5",
            "text": "क्या आपको कोई संगीत सुनाना है? मैं आपका पसंदीदा प्लेलिस्ट बजा सकता हूं या कुछ नया सुझा सकता हूं।",
            "phonetics": "Kya aapko koi sangeet sunana hai? Main aapka pasandida playlist baja sakta hoon ya kuch naya sujha sakta hoon.",
            "scenario": "Entertainment offer"
        }
    ]
}


# ==============================================================================
# AANKANSHA (FEMALE) - WARM, PROFESSIONAL VOICE
# Voice ID: 21m00Tcm4TlvDq8ikWAM (Rachel - ElevenLabs)
# ==============================================================================

AANKANSHA_NEPALI = {
    "greetings": [
        {
            "id": "ne_aa_greet_1",
            "text": "शुभ प्रभात प्रिय! म Aankansha हुँ, तपाईंको मित्रवत भ्वाइस सहायक। आजको दिन राम्रो होस्।",
            "phonetics": "Shubha prabhat priya! Ma Aankansha hum, tapaiko mitrwat bhvais sahayak. Aajko dina ramro hos.",
            "scenario": "Morning greeting"
        },
        {
            "id": "ne_aa_greet_2",
            "text": "नमस्ते प्रिय! तपाईंलाई भेटेर धेरै खुशी भयो। आज म तपाईंलाई कसरी मद्दत गर्ने छु?",
            "phonetics": "Namaste priya! Tapaikai bhete rai khusi bhayo. Aaj ma tapaikai kasari madad garne chhu?",
            "scenario": "General greeting"
        },
        {
            "id": "ne_aa_greet_3",
            "text": "शुभ दिउँसो प्रिय! कृपया आराम गर्नुहोस् र मलाई थाहा दिनुहोस् म तपाईंको लागि के गर्न सक्छु।",
            "phonetics": "Shubha diuso priya! Kripya aram garnuhos ra malai tha dinnuhos ma tapaiko lagi ke garna sakhchu.",
            "scenario": "Afternoon greeting"
        },
        {
            "id": "ne_aa_greet_4",
            "text": "शुभ साँझ प्रिय! दिन थकाई लाग्नुभयो नि हैन? आराम गर्नुहोस्, म यहाँ छु।",
            "phonetics": "Shubha sanjha priya! Dina thakai lagunubhayo ni haina? Aram garnuhos, ma yaha chhu.",
            "scenario": "Evening greeting"
        },
        {
            "id": "ne_aa_greet_5",
            "text": "हेलो प्रिय साथी! कस्तो छ आजको दिन? म तपाईंको साथमा छु।",
            "phonetics": "Hello priya sathi! Kasto chha aajko dina? Ma tapaiko satama chhu.",
            "scenario": "Casual greeting"
        }
    ],
    "weather": [
        {
            "id": "ne_aa_weather_1",
            "text": "प्रिय, हालको मौसम धेरै राम्रो छ। तापक्रम 22 डिग्री सेल्सियस छ, हल्का हावा चलिरहेको छ।",
            "phonetics": "Priya, halko mausam dherai ramro chha. Tapakraam 22 degree celsius chha, halka hawa chalirihako chha.",
            "scenario": "Weather update - pleasant"
        },
        {
            "id": "ne_aa_weather_2",
            "text": "आज दिउँसोभरि नै वर्षा हुने अपेक्षा छ प्रिय। कृपया छाता साथमा लिनुहोस्।",
            "phonetics": "Aaj diunsabhiri nai varsha hune apeksha chha priya. Kripya chhata satama linuhos.",
            "scenario": "Weather update - rainy"
        },
        {
            "id": "ne_aa_weather_3",
            "text": "आज घाम राम्रोसँग लागिरहेको छ प्रिय। 28 डिग्री सेल्सियस तापक्रम छ। बाहिर निस्कनुहोस् र मजा लिनुहोस्।",
            "phonetics": "Aaj gham ramrosanga lagirihako chha priya. 28 degree celsius tapakraam chha. Bahir niskunuhos ra maza linuhos.",
            "scenario": "Weather update - sunny"
        },
        {
            "id": "ne_aa_weather_4",
            "text": "भोलि बिहान हिम्मे हुनेछ प्रिय। दृश्यता धेरै कम हुनेछ। यात्रा गर्दा सावधान हुनुहोस्।",
            "phonetics": "Boli bihana himme hunechha priya. Drishyta dherai kam hunechha. Yatra garda savdhan hunuhos.",
            "scenario": "Weather update - foggy"
        },
        {
            "id": "ne_aa_weather_5",
            "text": "आज राति चिसो बढ्नेछ प्रिय। तापक्रम 15 डिग्री सेल्सियससम्म झर्नेछ। न्यानो कपडा लिनुहोस्।",
            "phonetics": "Aaj rati chiso badhnechha priya. Tapakraam 15 degree celsius samjha jharnetchha. Nyano kapda linuhos.",
            "scenario": "Weather update - cold"
        }
    ],
    "reminders": [
        {
            "id": "ne_aa_remind_1",
            "text": "अनुस्मारक प्रिय: तपाईंसँग 30 मिनटमा बैठक छ। म तपाईंलाई सम्झाइराख्छु।",
            "phonetics": "Anusmarak priya: Tapaaisanga 30 minutama baithak chha. Ma tapaikai samjhai rakchhu.",
            "scenario": "Meeting reminder"
        },
        {
            "id": "ne_aa_remind_2",
            "text": "प्रिय, घर जाने बाटोमा किराना किन्नुहोस्। तरकारी, फलफूल र दूध चाहिनेछ।",
            "phonetics": "Priya, ghar jane batoma kirana kinuhos. Tarakari, phalphul ra dudh chahinechha.",
            "scenario": "Shopping reminder"
        },
        {
            "id": "ne_aa_remind_3",
            "text": "प्रिय, तपाईंको औषधि भोलि सकिनेछ। कृपया समयमै लिनुहोस्।",
            "phonetics": "Priya, tapaiko aushadhi boli sakinechha. Kripya samayamai linuhos.",
            "scenario": "Health reminder"
        },
        {
            "id": "ne_aa_remind_4",
            "text": "जन्मदिन अनुस्मारक प्रिय: तपाईंको मित्रको भोलि जन्मदिन हो। शुभकामना पठाउनुहोस्!",
            "phonetics": "Janmadina anusmarak priya: Tapaiko mitrko boli janmadina ho. Shubhakamana pathaunuhos!",
            "scenario": "Birthday reminder"
        },
        {
            "id": "ne_aa_remind_5",
            "text": "बिल अनुस्मारक प्रिय: बिजुली बिल तिर्न बाँकी छ। 3 दिनभित्र तिर्नुहोस्।",
            "phonetics": "Bil anusmarak priya: Bijuli bil tirna baki chha. 3 dinabhitra tirnuhos.",
            "scenario": "Bill reminder"
        }
    ],
    "directions": [
        {
            "id": "ne_aa_direct_1",
            "text": "नजिकैको अस्पताल जानको लागि प्रिय, मुख्य चोकमा दायाँ मोड्नुहोस् र 500 मिटर सोझै जानुहोस्।",
            "phonetics": "Najikko aspatal janko lagi priya, mukhya chokma dayan modnuhos ra 500 meter sojha januhos.",
            "scenario": "Directions to hospital"
        },
        {
            "id": "ne_aa_direct_2",
            "text": "बस स्टेशन करिब 2 किलोमिटर टाढा छ प्रिय। उत्तरतर्फ जानुहोस्, घडी टावर नजिकै हुनेछ।",
            "phonetics": "Bas station karib 2 kilometar tadha chha priya. Uttartatrab januhos, ghadi tower najikko hunechha.",
            "scenario": "Directions to bus station"
        },
        {
            "id": "ne_aa_direct_3",
            "text": "किनमेल मल जानको लागि प्रिय, पूर्वी हाइवे लिनुहोस्। तेस्रो टोल गेटबाट निस्कनुहोस्।",
            "phonetics": "Kinamal mala janko lagi priya, purbi highway linuhos. Tesro tol gate bata niskunuhos.",
            "scenario": "Directions to mall"
        },
        {
            "id": "ne_aa_direct_4",
            "text": "नजिकैको ATM यहीँ कोनामा छ प्रिय। 100 मिटर तल दायाँपट्टि हुनेछ।",
            "phonetics": "Najikko ATM yihin konama chha priya. 100 meter tal dayanpatti hunechha.",
            "scenario": "Directions to ATM"
        },
        {
            "id": "ne_aa_direct_5",
            "text": "हवाई अड्डा जानको लागि प्रिय, expressway राम्रो विकल्प हो। 25 मिनट लाग्नेछ।",
            "phonetics": "Hawai adda janko lagi priya, expressway ramro vikalp ho. 25 minut lagnechha.",
            "scenario": "Directions to airport"
        }
    ],
    "general": [
        {
            "id": "ne_aa_gen_1",
            "text": "मैले तपाईंको कार्य थपें प्रिय। अरू केही मद्दत चाहनुहुन्छ?",
            "phonetics": "Maile tapaiko kary thapay priya. Aaru kehi madad chahānuhunchha?",
            "scenario": "Task completion"
        },
        {
            "id": "ne_aa_gen_2",
            "text": "नजिकैका राम्रा रेस्टुरेन्टहरू खोजें प्रिय। के तपाईंलाई सुचाउने?",
            "phonetics": "Najikka ramra restaurant haru khojay priya. Ke tapaikai suchaune?",
            "scenario": "Restaurant search"
        },
        {
            "id": "ne_aa_gen_3",
            "text": "तपाईंको भोलिको तालिका धेरै व्यस्त छ प्रिय। 5 वटा बैठकहरू छन्। तयारीमा मद्दत गर्ने छु।",
            "phonetics": "Tapaiko boliko talika dherai vyast chha priya. 5 vata baithak haru chhan. Tayari ma madad garne chhu.",
            "scenario": "Schedule review"
        },
        {
            "id": "ne_aa_gen_4",
            "text": "इमेल पठाएँ प्रिय। अरू केही सहायता चाहनुहुन्छ?",
            "phonetics": "Email pathayen priya. Aaru kehi sahayata chahānuhunchha?",
            "scenario": "Email assistance"
        },
        {
            "id": "ne_aa_gen_5",
            "text": "के संगीत सुन्न चाहनुहुन्छ प्रिय? म तपाईंलाई राम्रो playlist बजाउने छु।",
            "phonetics": "Ke sangeet sunna chahānuhunchha priya? Ma tapaikai ramro playlist bajaune chhu.",
            "scenario": "Entertainment offer"
        }
    ]
}


# ==============================================================================
# VOICE SAMPLE GENERATION MAPPING
# ==============================================================================

VOICE_SAMPLES = {
    "aabinash": {
        "english": AABINASH_ENGLISH,
        "nepali": AABINASH_NEPALI,
        "hindi": AABINASH_HINDI
    },
    "aankansha": {
        "nepali": AANKANSHA_NEPALI
    }
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_all_samples():
    """Get all voice samples organized by assistant"""
    return VOICE_SAMPLES


def get_samples_by_assistant(assistant_name):
    """Get samples for a specific assistant"""
    return VOICE_SAMPLES.get(assistant_name.lower(), {})


def get_samples_by_language(assistant_name, language):
    """Get samples for a specific assistant and language"""
    assistant = VOICE_SAMPLES.get(assistant_name.lower(), {})
    return assistant.get(language.lower(), {})


def get_samples_by_scenario(assistant_name, language, scenario):
    """Get samples for a specific assistant, language, and scenario"""
    lang_samples = get_samples_by_language(assistant_name, language)
    return lang_samples.get(scenario.lower(), [])


def get_all_texts_for_voice(assistant_name, language):
    """Get all text content for a specific voice and language (flat list)"""
    samples = get_samples_by_language(assistant_name, language)
    all_texts = []
    for scenario, items in samples.items():
        for item in items:
            all_texts.append(item["text"])
    return all_texts


if __name__ == "__main__":
    # Print sample summary
    print("=" * 70)
    print("VOICE SAMPLE CONTENT SUMMARY")
    print("=" * 70)
    
    for assistant, languages in VOICE_SAMPLES.items():
        print(f"\n{assistant.upper()}")
        print("-" * 40)
        for language, scenarios in languages.items():
            total_samples = sum(len(items) for items in scenarios.values())
            print(f"  {language.capitalize()}: {total_samples} samples")
            for scenario, items in scenarios.items():
                print(f"    - {scenario}: {len(items)} samples")
    
    print("\n" + "=" * 70)
    print("Total voice samples ready for synthesis")
    print("=" * 70)
