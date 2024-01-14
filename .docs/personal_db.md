# jjugg - An Intelligent Copilot for Job Hunting

## profile_management
Manages Profile, Resumes, Skills, And Full Context of What I Offer and My Capabilities

### personal_information
1. `id` SERIAL PRIMARY KEY
2. `first_name` VARCHAR(50)
3. `last_name` VARCHAR(50)
4. `date_of_birth` DATE
5. `phone_number` VARCHAR(15)
6. `email_address` VARCHAR(100)

### personal_summaries
1. `id` SERIAL PRIMARY KEY
2. `type` ENUM('professional', 'technical', 'lax', 'colloquial')
3. `note` TEXT
4. `body` TEXT

### personal_headlines
1. `id` SERIAL PRIMARY KEY
2. `body` TEXT
3. `type` ENUM('professional', 'technical', 'lax', 'colloquial')
4. `note` TEXT

### skills
1. `id` SERIAL PRIMARY KEY
2. `type` ENUM('soft', 'hard')
3. `category` ENUM('automation', 'front end web dev', 'backend web dev', 'blogging', 'social media', 'agi', 'etc...')
4. `name` VARCHAR(100)
5. `note` TEXT

## job_tracking_system
Tracks Jobs, Freelancing Gigs, and Everything Associated With It

### jobs
1. `job_id` SERIAL PRIMARY KEY
2. `title` VARCHAR(100)
3. `description` TEXT
4. `posted_date` DATE
5. `location` VARCHAR(100)
6. `type` ENUM('full-time', 'part-time', 'contract', 'internship')

### applications
1. `application_id` SERIAL PRIMARY KEY
2. `job_id` INTEGER REFERENCES jobs(job_id)
3. `user_id` INTEGER REFERENCES personal_information(id)
4. `application_date` DATE
5. `status` ENUM('applied', 'interview', 'offer', 'rejected')

## online_presence_management
Manages Online Presence and Updates Online Profiles

### social_media_profiles
1. `profile_id` SERIAL PRIMARY KEY
2. `user_id` INTEGER REFERENCES personal_information(id)
3. `platform` ENUM('linkedin', 'github', 'twitter', 'facebook')
4. `profile_url` VARCHAR(255)

## event_management
Tracks Database Activity

### events
1. `event_id` SERIAL PRIMARY KEY
2. `user_id` INTEGER REFERENCES personal_information(id)
3. `event_name` VARCHAR(100)
4. `event_date` TIMESTAMP
5. `event_description` TEXT

## timeline_tracking
Tracks Timeline and History of My Life in Various Angles (Technical, Real, Professional, Magnum Opus)

### timeline
1. `timeline_id` SERIAL PRIMARY KEY
2. `user_id` INTEGER REFERENCES personal_information(id)
3. `start_date` DATE
4. `end_date` DATE
5. `description` TEXT

# prozhyk - An Intelligent Copilot for Project Management, Branding, Planning, and Extrapolation

## branding_management
Manage Branding, Copy, Online Presence, of Projects

### branding
1. `brand_id` SERIAL PRIMARY KEY
2. `name` VARCHAR(100)
3. `logo_url` VARCHAR(255)
4. `color_palette` JSONB

## timeline_management
Tracks and Plans the Timelines of Projects Autonomously Using GPT API

### project_timeline
1. `timeline_id` SERIAL PRIMARY KEY
2. `project_id` INTEGER REFERENCES projects(project_id)
3. `start_date` DATE
4. `end_date` DATE
5. `milestones` JSONB

## extrapolation_management
Extrapolates on Project Features and Ideas Using GPT API

### project_extrapolations
1. `extrapolation_id` SERIAL PRIMARY KEY
2. `project_id` INTEGER REFERENCES projects(project_id)
3. `extrapolation_date` DATE
4. `extrapolation_data` JSONB

## project_management
Manages Projects, Features, Capabilities, Etc

### projects
1. `project_id` SERIAL PRIMARY KEY
2. `title` VARCHAR(100)
3. `type` ENUM('cli', 'web app', 'static site', 'library')
4. `short_description` TEXT

### project_descriptions
1. `description_id` SERIAL PRIMARY KEY
2. `project_id` INTEGER REFERENCES projects(project_id)
3. `size` ENUM('short', 'long')
4. `text` TEXT
5. `type` ENUM('professional', 'technical', 'lax', 'colloquial')

## event_management
Tracks DB Activity

### project_events
1. `event_id` SERIAL PRIMARY KEY
2. `project_id` INTEGER REFERENCES projects(project_id)
3. `event_name` VARCHAR(100)
4. `event_date` TIMESTAMP
5. `event_description` TEXT
