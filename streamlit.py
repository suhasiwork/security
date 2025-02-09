import os
import subprocess
import git
import shutil
import streamlit as st
import time

def clone_repo(repo_url, clone_dir):
    """
    Clone a Git repository to a specified directory.
    """
    if os.path.exists(clone_dir):
        try:
            shutil.rmtree(clone_dir)  # Remove the existing repo folder
            st.warning(f"Deleted existing repository directory: {clone_dir}")
        except PermissionError as e:
            st.error(f"PermissionError: Unable to delete {clone_dir}. Make sure no files are in use.")
            raise e
    st.info(f"Cloning the repository from {repo_url}...")
    git.Repo.clone_from(repo_url, clone_dir)
    st.success(f"Repository cloned to {clone_dir}")

def parse_bandit_report(report_path):
    """
    Parse the Bandit report and extract a summary of vulnerabilities.
    """
    if not os.path.exists(report_path):
        return {"total_issues": 0, "execution_time": "N/A"}, ""
    
    total_issues = 0
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
        total_issues = report_content.count("Issue:")
    
    return {"total_issues": total_issues, "execution_time": "Completed"}, report_content

def run_bandit(clone_dir):
    """
    Run Bandit on the cloned repository to check for security vulnerabilities.
    """
    st.info("Running Bandit to check for security vulnerabilities...")
    report_path = "bandit_report.txt"
    
    start_time = time.time()
    subprocess.run(['bandit', '-r', clone_dir, '-f', 'txt', '-o', report_path], 
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    execution_time = round(time.time() - start_time, 2)
    
    summary, report_content = parse_bandit_report(report_path)
    summary["execution_time"] = f"{execution_time} sec"
    
    st.success("Bandit scan completed successfully.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Issues", value=summary["total_issues"])
    with col2:
        st.metric(label="Execution Time", value=summary["execution_time"])
    
    st.markdown("### Detailed Bandit Report")
    st.text_area("Report", report_content, height=400)

def main():
    st.title("Git Repository Security Scanner")
    
    repo_url = st.text_input("Enter the GitHub repository URL:", "https://github.com/django/django.git")
    clone_dir = "cloned_repo"

    if st.button("Start Scan"):
        try:
            clone_repo(repo_url, clone_dir)
        except PermissionError:
            st.stop()
        
        run_bandit(clone_dir)

if __name__ == "__main__":
    main()
