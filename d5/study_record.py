class StudyRecord:
    unit = "分钟"

    def __init__(self, topic):
        self.topic = topic
        self.sessions = []

    def session_count(self):
        return len(self.sessions)

    
    def add_session(self, session):
        self.sessions.append(session)

    def total_minutes(self):
        total = 0
        for minutes in self.sessions:
            total += minutes    


        return total



    

