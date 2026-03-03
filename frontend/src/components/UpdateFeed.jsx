export default function UpdateFeed({ challenge, firedUpdates, newlyFiredIds }) {
  const updates = challenge?.requirements_updates || [];
  const firedData = updates.filter((u) => firedUpdates.includes(u.id));

  if (firedData.length === 0) return null;

  return (
    <div className="update-feed">
      {firedData.map((update) => {
        const isNew = newlyFiredIds.includes(update.id);
        const count = update.additional_test_cases?.length || 0;
        return (
          <div
            key={update.id}
            className={`update-bubble${isNew ? " update-bubble-new" : ""}`}
          >
            <div className="update-bubble-header">
              <span className="update-sender">💬 {update.sender}</span>
              <span className="update-badge">
                +{count} test{count !== 1 ? "s" : ""}
              </span>
            </div>
            <p className="update-message">"{update.message}"</p>
          </div>
        );
      })}
    </div>
  );
}
