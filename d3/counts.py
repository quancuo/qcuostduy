

def count_topics(topics):
    topic_count = {}
    for x in topics:
        if x in topic_count:
            topic_count[x] += 1
        else:
            topic_count[x] = 1
    return topic_count

topics = ["Python", "Java", "Python", "Git", "Python"]


print(count_topics(topics))

