import React from 'react';
import ProfileForm from '../components/forms/ProfileForm';

const ProfilePage: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Perfil do Usuário</h1>
      <ProfileForm />
    </div>
  );
};

export default ProfilePage;
