# Medical-API
A REST API that fetches medical symptoms, diagnosis and treatment options and stores them in a database.

Apimedic's APIs was used to fetch symptoms and issues along with their treatment options. The data is stored in a database (NoSQL).

The stored data can be accessed through some built-in queries.

A list of nearby doctors can be accessed by entering the user's address.

The user can also enter text like "I'm having back pain" and receive the medical conditions associated with it.

NOTE: The command python -m spacy download en

The implemented functionalities are:-

    Fetch_Symptoms - This class fetches a list of medical symptoms and stores them in a database. The user can view the symptoms as well.

    eg. <ip_address>/fetch_symptoms

    Get_Medical_Condition - This class gives the possible medical conditions/diagnosis based on the symptoms given by the user. It takes 1 argument:
        symptoms: The symptoms for which the diagnosis is required.
        
    eg. <ip_address>/get_medical_condition/Anxiety, Vomiting

    Fetch_Issues: This class fetches a list of medical issues and stores them in a database. The user can view the symptoms as well.

    eg. <ip_address>/fetch_issues

    Treatment: This class gives the treatment description for a medical condition given by the user. It takes one argument:
        issue: The medical condition for which treatment is required.
        
    eg. <ip_address>/treatment/Flu

    Get_Nearby_Doctors: This class gives a list of doctors that are nearest to the user based on the address given by them. It takes 1 argument:
        address: The address given by the user.

    eg. <ip_address>/get_nearby_doctors/Nucleus Mall, Ranchi

    Tell_Your_Problem: This class extracts symptoms from text like "i'm having back pain" entered by the user and returns the possible medical condition. It takes 1 argument:
    problem: The text describing the user's problem

    eg. <ip_address>/tell_your_problem/i keep coughing
