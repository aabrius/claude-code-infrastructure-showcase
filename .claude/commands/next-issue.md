# Next Issue

You will start to work on the next issue from Linear.

You will be given one or more issues IDs to work on in the $ARGUMENTS.

First, you will check the issue details in Linear using the Linear MCP using these info:

1. **Project Name**: GAM-API
2. **Project ID**: c56e5780-3a46-40ee-b43d-c6a60100e3af
3. **Team ID**: 1985867d-a86d-4d9e-b537-a3ac296846f2

**IMPORTANT**: You can ALWAYS run up to 5 multiple agents in parallel to work on the issue if you think it will be better each with a different task.

## Linear Issue Update Consistency Rules

**CRITICAL**: When completing ANY Linear issue, ALWAYS maintain consistency across related issues:

1. **Check ALL related issues** before marking any task complete:

   - Parent issues (if working on subtasks)
   - Sibling issues (other subtasks in the same parent)
   - Child issues (if completing a parent task)

2. **Apply SAME documentation standard** to ALL completed issues:

   - Detailed completion summaries with ✅ checkboxes
   - List of files created/modified with descriptions
   - Features implemented section
   - Next steps or configuration requirements
   - Clear status indicators (e.g., "✅ COMPLETED", "✅ DELIVERED")

3. **Update parent issues** when all subtasks are complete:

   - Mark all acceptance criteria as completed [x]
   - Add comprehensive summary of all completed subtasks
   - Include final implementation status
   - Reference all completed subtask IDs

4. **Documentation Quality Examples**:
   - ✅ Good: "AA-204: Detailed completion with files, features, implementation notes"
   - ❌ Poor: "AA-201, AA-202, AA-203: Just marked Done without detailed updates"

**Why this matters**: Inconsistent documentation makes it hard to track what was actually delivered and creates confusion about project status.

**IMPORTANT**: When querying Linear issues:

- Use `projectId` parameter with the project ID (c56e5780-3a46-40ee-b43d-c6a60100e3af)
- Do NOT use project ID as `teamId` - they are different entities
- Always include `limit` parameter to avoid token overflow (max 50)

## Linear Status IDs

Always use the status IDs below when querying Linear.

**Unstarted:**

- ID: 4e1283f8-5810-4e83-838f-b6b7640c1e48 - Status name: Todo

**Started:**

- ID: a62510c2-78bf-43bf-b863-771660146c2d - Status name: In Progress
- ID: a63335a6-0301-4c0d-83e2-3a7d99f67954 - Status name: In Review

**Completed:**

- ID: 79fbe641-6b5e-4b79-8f63-6cffb62c3f75 - Status name: Done

**Canceled:**

- ID: 42570729-f9f7-4ef2-984f-d9d0f57787e2 - Status name: Canceled
- ID: e5b47793-ed73-428c-873f-785fa74ed449 - Status name: Duplicate

**Other:**

- ID: eb28e97c-9081-474d-80e3-dd0ccc4f149b - Status name: Triage
- ID: b2fe2370-ac61-463b-a267-c4a30304d66f - Status name: Backlog

## Instructions

1. Read the issue and understand the requirements before starting to work on it.
2. Think about the complexity of the issue and see if it's better to break it down into smaller issues.
3. If the issue is complex, you will need to break it down into smaller issues and run multiple agents to work on them at the same time.
4. You will need to update the issue status in Linear to "In Progress" when you start to work on it.
5. You will never finish an issue without updating the issue status in Linear to "Done".
6. When you create a new doc about any issue or implementation, save is as document in Linear and link it to the issue along with saving it in the @docs/ in the right folder.

## Workflow

### Step 1: Read the issue and understand the requirements before starting to work on it

- Read the issue and search for related files in the codebase you will need to work on.
- Update the issue status in Linear to "In Progress" after you create a plan and evaluate the options to implement the issue.
- Create a comment in the issue with the plan and the options you evaluated.

### Step 2: Start to work on the issue

- Read the files and understand the codebase.
- If neeeded, use the Context7 MCP to get the latest information about any package or service for actual documentation.
- Write clear, modular TypeScript code with proper type definitions
- Don't create tests files if the issue dont mention it
- ALWAYS review the task and search for any possible gaps or missing information before move it to Done or In Review

### Step 3: Review the code and update the issue status in Linear

- Review if the code is respecting the maximum lines of a single file of 500 lines
- Check if the issue is complete and all the requirements are met
- Update the issue status and add a comment in the issue with the results of the review
