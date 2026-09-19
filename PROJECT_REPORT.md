# Project Report — AI-Based Lost & Found Intelligence Center

## Abstract
The AI-Based Lost & Found Intelligence Center is a desktop computer-vision application designed to help users identify potentially matching found objects from a lost-item photograph. It combines structured item reporting, SQLite persistence, managed image storage and hybrid visual similarity ranking.

## Problem Statement
Manual lost-and-found operations depend heavily on text descriptions. Different users may describe the same object differently. Image-based comparison provides an additional signal that can reduce the effort required to review found-item reports.

## Proposed Solution
The system stores lost and found reports and their images. When a lost-item image is selected, the matching engine evaluates all active found images and returns the top five candidates.

## System Modules
1. Dashboard
2. Lost Item Reporting
3. Found Item Reporting
4. Image Match Engine
5. Records/Search
6. Status Management
7. CSV Reporting
8. SQLite Data Layer

## Algorithm
The system uses ORB local descriptors and an HSV color histogram. ORB contributes 75% of the final score and color similarity contributes 25%.

## Limitations
- It is not a trained neural-network model.
- Similar-looking objects can produce false positives.
- Poor lighting, severe rotation, occlusion or very different viewpoints can reduce matching quality.
- A score must be treated as a ranking signal rather than a probability.

## Testing Checklist
- [ ] Report a lost item without an image → validation should block submission.
- [ ] Report a found item → image and database record should be created.
- [ ] Add duplicate image filenames → application should rename safely.
- [ ] Run AI Match with found images → top candidates should be ranked.
- [ ] Search Records → matching records should be filtered.
- [ ] Mark a record Resolved → status should change.
- [ ] Export CSV → report should open in Excel.
- [ ] Run project from another working directory → project-relative paths should continue to work.

## Viva Questions
### Why ORB?
ORB is fast, patent-free and suitable for local feature matching in a desktop demonstration.

### Why HSV histogram?
HSV separates hue/saturation information and provides a useful global color similarity signal.

### Is the score a probability?
No. It is a weighted visual similarity/ranking score.

### Why SQLite?
SQLite is serverless, lightweight and appropriate for a standalone desktop application.

### How can the project become a real AI system?
Use a pretrained deep-learning image embedding model and vector similarity search, then evaluate it on a labeled lost/found dataset.

## Future Enhancement Roadmap
- REST API
- Web/mobile front end
- Authentication and role-based access
- MySQL/PostgreSQL
- Deep-learning embeddings
- Vector database
- Geolocation
- Notification service
- Analytics and audit logs
