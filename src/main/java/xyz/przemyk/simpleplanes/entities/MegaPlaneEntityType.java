package xyz.przemyk.simpleplanes.entities;

import net.minecraft.entity.EntityDimensions;

public class MegaPlaneEntityType extends AbstractPlaneEntityType<MegaPlaneEntity> {

    public MegaPlaneEntityType() {
        super(MegaPlaneEntity::new, MegaPlaneEntity.FLYING_SIZE);
    }
}
