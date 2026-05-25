import { useEffect, useState } from "react";
import { supabase } from "../services/supabaseClient";

export default function ProfileKnowledge() {
  const [profile, setProfile] = useState(null);
  const [skills, setSkills] = useState([]);
  const [chunks, setChunks] = useState([]);

  useEffect(() => {
    if (!supabase) return;
    async function load() {
      const { data: profiles } = await supabase.from("user_profiles").select("*").limit(1);
      const p = profiles?.[0];
      setProfile(p);
      if (!p) return;
      const { data: sk } = await supabase.from("profile_skills").select("*").eq("profile_id", p.id);
      const { data: ch } = await supabase
        .from("profile_knowledge_chunks")
        .select("*")
        .eq("profile_id", p.id);
      setSkills(sk || []);
      setChunks(ch || []);
    }
    load();
  }, []);

  return (
    <div>
      <h2>Profile Knowledge</h2>
      {profile ? (
        <>
          <h3>{profile.display_name}</h3>
          <p className="muted">{profile.headline}</p>
          <p>{profile.summary}</p>
          <h4>Skills</h4>
          <ul>
            {skills.map((s) => (
              <li key={s.id}>
                {s.skill_name} ({s.proficiency})
              </li>
            ))}
          </ul>
          <h4>RAG chunks</h4>
          {chunks.map((c) => (
            <div key={c.id} className="chunk-card">
              <strong>{c.title}</strong>
              <p>{c.content}</p>
            </div>
          ))}
        </>
      ) : (
        <p className="muted">No profile seeded. Run python scripts/seed_profile.py</p>
      )}
    </div>
  );
}
