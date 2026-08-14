import { useEffect, useState } from "react";
import { getWorkflowAnalysis } from "../services/workflowApi";
import "./WorkflowExplorer.css";

function WorkflowExplorer() {
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadWorkflows() {
      try {
        const result = await getWorkflowAnalysis();

        console.log(
          "Workflow Explorer Response:",
          result
        );

        setWorkflows(result.workflows || []);
      } catch (err) {
        console.error(
          "Workflow Explorer error:",
          err
        );

        setError(
          "Unable to load workflow data."
        );
      } finally {
        setLoading(false);
      }
    }

    loadWorkflows();
  }, []);

  const filteredWorkflows =
    workflows.filter((workflow) => {

      const matchesSearch =
        workflow.ticket_id
          ?.toLowerCase()
          .includes(search.toLowerCase()) ||
        workflow.title
          ?.toLowerCase()
          .includes(search.toLowerCase()) ||
        workflow.assignee
          ?.toLowerCase()
          .includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "All" ||
        workflow.status === statusFilter;

      const matchesPriority =
        priorityFilter === "All" ||
        workflow.priority === priorityFilter;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesPriority
      );
    });

  if (loading) {
    return (
      <div className="workflow-explorer-state">
        Loading workflow explorer...
      </div>
    );
  }

  if (error) {
    return (
      <div className="workflow-explorer-state">
        {error}
      </div>
    );
  }

  return (
    <div className="workflow-explorer">

      {/* HEADER */}

      <div className="workflow-explorer-header">

        <div>
          <span className="page-eyebrow">
            WORKFLOW INTELLIGENCE
          </span>

          <h1>
            Workflow Explorer
          </h1>

          <p>
            Explore Jira workflows, identify
            delays, and inspect ticket-level
            operational intelligence.
          </p>
        </div>

        <div className="workflow-count">

          <strong>
            {workflows.length}
          </strong>

          <span>
            Workflows
          </span>

        </div>

      </div>


      {/* FILTER BAR */}

      <div className="workflow-toolbar">

        <input
          type="text"
          placeholder="Search ticket, title or assignee..."
          value={search}
          onChange={(e) =>
            setSearch(e.target.value)
          }
          className="workflow-search"
        />

        <select
          value={statusFilter}
          onChange={(e) =>
            setStatusFilter(e.target.value)
          }
        >
          <option value="All">
            All Status
          </option>

          <option value="To Do">
            To Do
          </option>

          <option value="In Progress">
            In Progress
          </option>

          <option value="In Review">
            In Review
          </option>

          <option value="Done">
            Done
          </option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) =>
            setPriorityFilter(e.target.value)
          }
        >
          <option value="All">
            All Priority
          </option>

          <option value="High">
            High
          </option>

          <option value="Medium">
            Medium
          </option>

          <option value="Unknown">
            Unknown
          </option>
        </select>

      </div>


      {/* MAIN CONTENT */}

      <div className="workflow-content">

        <div className="workflow-list">

          <div className="workflow-list-header">

            <span>
              {filteredWorkflows.length} workflows found
            </span>

          </div>

          {filteredWorkflows.length === 0 ? (

            <div className="empty-workflows">
              No workflows match your filters.
            </div>

          ) : (

            filteredWorkflows.map(
              (workflow) => (

                <div
                  key={workflow.ticket_id}
                  className={
                    selectedWorkflow?.ticket_id ===
                    workflow.ticket_id
                      ? "workflow-card selected"
                      : "workflow-card"
                  }
                  onClick={() =>
                    setSelectedWorkflow(
                      workflow
                    )
                  }
                >

                  <div className="workflow-card-top">

                    <span className="ticket-id">
                      {workflow.ticket_id}
                    </span>

                    <span
                      className={`priority-badge priority-${workflow.priority?.toLowerCase()}`}
                    >
                      {workflow.priority}
                    </span>

                  </div>

                  <h3>
                    {workflow.title}
                  </h3>

                  <div className="workflow-meta">

                    <span>
                      {workflow.status}
                    </span>

                    <span>
                      {workflow.assignee}
                    </span>

                  </div>

                  <div className="workflow-card-bottom">

                    <span>
                      Waiting:
                      <strong>
                        {" "}
                        {workflow.days_waiting}
                        {" "}
                        days
                      </strong>
                    </span>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();

                        setSelectedWorkflow(
                          workflow
                        );
                      }}
                    >
                      View Details →
                    </button>

                  </div>

                </div>

              )
            )

          )}

        </div>


        {/* DETAIL PANEL */}

        <div className="workflow-detail">

          {!selectedWorkflow ? (

            <div className="detail-placeholder">

              <div className="detail-placeholder-icon">
                ◈
              </div>

              <h2>
                Select a workflow
              </h2>

              <p>
                Select a ticket from the list
                to inspect its workflow details.
              </p>

            </div>

          ) : (

            <>

              <div className="detail-header">

                <div>

                  <span className="ticket-id">
                    {selectedWorkflow.ticket_id}
                  </span>

                  <h2>
                    {selectedWorkflow.title}
                  </h2>

                </div>

                <span
                  className={`priority-badge priority-${selectedWorkflow.priority?.toLowerCase()}`}
                >
                  {selectedWorkflow.priority}
                </span>

              </div>


              <div className="detail-status">

                <span>
                  Status
                </span>

                <strong>
                  {selectedWorkflow.status}
                </strong>

              </div>


              <div className="detail-grid">

                <div className="detail-item">
                  <span>
                    Assignee
                  </span>

                  <strong>
                    {selectedWorkflow.assignee}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>
                    Waiting Time
                  </span>

                  <strong>
                    {selectedWorkflow.days_waiting} days
                  </strong>
                </div>


                <div className="detail-item">
                  <span>
                    Due Date
                  </span>

                  <strong>
                    {selectedWorkflow.due_date || "Not set"}
                  </strong>
                </div>


                <div className="detail-item">
                  <span>
                    Created
                  </span>

                  <strong>
                    {selectedWorkflow.created_at
                      ? new Date(
                          selectedWorkflow.created_at
                        ).toLocaleDateString()
                      : "Unknown"}
                  </strong>
                </div>

              </div>


              <div className="detail-section">

                <span className="detail-section-label">
                  WORKFLOW SIGNAL
                </span>

                <h3>
                  Operational waiting time
                </h3>

                <p>
                  This ticket has been waiting for{" "}
                  <strong>
                    {selectedWorkflow.days_waiting}
                    {" "}
                    days
                  </strong>
                  . Extended waiting time may
                  indicate a workflow bottleneck
                  requiring investigation.
                </p>

              </div>


              <div className="detail-section recommendation-box">

                <span className="detail-section-label">
                  RECOMMENDED ACTION
                </span>

                <p>
                  Review this ticket's current
                  workflow state and investigate
                  whether an approval, dependency,
                  or assignment is causing the delay.
                </p>

              </div>

            </>

          )}

        </div>

      </div>

    </div>
  );
}

export default WorkflowExplorer;